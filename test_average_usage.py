import io
import os
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout, redirect_stderr

import average_usage as au


class TestElectricityUsageAnalyzerUnit(unittest.TestCase):
    def setUp(self):
        self.analyzer = au.ElectricityUsageAnalyzer()

    def test_process_row_valid(self):
        row = {
            "Date": "09/29/2025",       # Monday
            "Start Time": "01:15 AM",   # hour=1 -> window 0
            "Consumption": "2.5",
        }
        result = self.analyzer.process_row(row)
        self.assertIsNotNone(result)
        day, window, kwh = result
        self.assertEqual(day, 0)        # Monday
        self.assertEqual(window, 0)     # 00:00–02:00 window
        self.assertAlmostEqual(kwh, 2.5)

    def test_process_row_malformed_increments_counter(self):
        bad_rows = [
            {"Date": "BadDate", "Start Time": "01:15 AM", "Consumption": "1.0"},  # bad date
            {"Date": "09/29/2025", "Start Time": "01:15 AM"},                     # missing consumption
            {"Start Time": "01:15 AM", "Consumption": "1.0"},                     # missing date
            {"Date": "09/29/2025", "Start Time": "01:15", "Consumption": "1.0"},  # bad time format
        ]
        for r in bad_rows:
            self.assertIsNone(self.analyzer.process_row(r))
        self.assertEqual(self.analyzer.get_malformed_rows_count(), len(bad_rows))

    def test_process_csv_data_aggregates_by_day_and_window(self):
        rows = [
            {"Date": "09/29/2025", "Start Time": "12:05 AM", "Consumption": "1.0"},  # Mon, window 0
            {"Date": "09/29/2025", "Start Time": "01:15 AM", "Consumption": "3.0"},  # Mon, window 0
            {"Date": "09/30/2025", "Start Time": "10:30 PM", "Consumption": "5.0"},  # Tue, window 22
        ]
        self.analyzer.process_csv_data(rows)
        self.assertEqual(self.analyzer.weekly_usage[0][0], [1.0, 3.0])
        self.assertEqual(self.analyzer.weekly_usage[1][22], [5.0])

    def test_calculate_averages_includes_zero_for_empty_windows(self):
        rows = [
            {"Date": "09/29/2025", "Start Time": "12:05 AM", "Consumption": "1.0"},
            {"Date": "09/29/2025", "Start Time": "01:15 AM", "Consumption": "3.0"},
        ]
        self.analyzer.process_csv_data(rows)
        averages = self.analyzer.calculate_averages()
        # Monday, 00:00–02:00 average (1.0 + 3.0)/2 = 2.0
        self.assertAlmostEqual(averages[0][0], 2.0)
        # A window with no data should be 0.0
        self.assertAlmostEqual(averages[0][2], 0.0)
        self.assertAlmostEqual(averages[6][22], 0.0)  # Sunday, any window = 0.0

    def test_format_time_window_label_leading_zero_and_midnight_handling(self):
        # 00 -> "12:00 AM - 2:00 AM"
        self.assertEqual(au.format_time_window_label(0), "12:00 AM - 2:00 AM")
        # 2 -> "2:00 AM - 4:00 AM" (no leading zero)
        self.assertEqual(au.format_time_window_label(2), "2:00 AM - 4:00 AM")
        # 22 -> "10:00 PM - 12:00 AM" (special-cased midnight end)
        self.assertEqual(au.format_time_window_label(22), "10:00 PM - 12:00 AM")

    def test_format_output_table_structure_and_values(self):
        # Build a minimal averages dict with one non-zero and rest zeros
        averages = {day: {h: 0.0 for h in au.TIME_WINDOWS} for day in range(7)}
        averages[0][0] = 2.0     # Monday, 00–02
        averages[1][22] = 5.0    # Tuesday, 22–24
        table = au.format_output_table(averages)

        lines = table.splitlines()
        # First line is the blank+title line (starts with "")
        self.assertTrue(lines[0].startswith(""))
        self.assertIn("Average Energy Consumption (kWh) by Time and Day of Week", lines[1])

        # Header contains "Time Window" and all days
        self.assertIn("Time Window", lines[3])
        for day_name in au.DAYS_OF_WEEK:
            self.assertIn(day_name, lines[3])

        # There is one dashed line after header
        self.assertTrue(set(lines[4]) <= {"-"})

        # There should be one data row per 2-hour window
        data_rows = lines[5:]
        self.assertEqual(len(data_rows), len(au.TIME_WINDOWS))

        # Check a couple of row values (formatted to 4 decimals, centered)
        # Row for 00:00–02:00 should include Monday's 2.0000 and others 0.0000
        first_row = data_rows[0]
        self.assertIn("12:00 AM - 2:00 AM", first_row)
        self.assertIn(f"{2.0:^12.4f}", first_row)  # Monday column
        # Row for 22:00–00:00 should include Tuesday's 5.0000
        last_row = data_rows[-1]
        self.assertIn("10:00 PM - 12:00 AM", last_row)
        self.assertIn(f"{5.0:^12.4f}", last_row)


class TestReadCsvFile(unittest.TestCase):
    def test_read_csv_file_success(self):
        content = textwrap.dedent("""\
            Date,Start Time,Consumption
            09/29/2025,12:00 AM,1.0
            09/29/2025,12:15 AM,2.0
        """)
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "data.csv")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            data, err = au.read_csv_file(path)
            self.assertIsNone(err)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["Consumption"], "1.0")

    def test_read_csv_file_error(self):
        data, err = au.read_csv_file("does/not/exist.csv")
        self.assertEqual(data, [])
        self.assertIsInstance(err, str)
        self.assertTrue(err)


class TestAnalyzeElectricUsageIntegration(unittest.TestCase):
    def test_analyze_electric_usage_happy_path_and_malformed_reporting(self):
        # Two Monday entries in window 0 (avg 2.0), one Tuesday entry in window 22 (avg 5.0)
        # Plus two malformed rows.
        content = textwrap.dedent("""\
            Date,Start Time,Consumption
            09/29/2025,12:00 AM,1.0
            09/29/2025,01:15 AM,3.0
            09/30/2025,10:30 PM,5.0
            09/29/2025,01:15 AM,   # malformed consumption
            BadDate,01:00 AM,1.2
        """)

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "data.csv")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            out = io.StringIO()
            err = io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                au.analyze_electric_usage(path)

            stdout = out.getvalue()
            stderr = err.getvalue()

            # Table presence & header
            self.assertIn("Average Energy Consumption (kWh) by Time and Day of Week", stdout)
            for day_name in au.DAYS_OF_WEEK:
                self.assertIn(day_name, stdout)

            # Specific row checks
            self.assertIn("12:00 AM - 2:00 AM", stdout)
            self.assertIn(f"{2.0:^12.4f}", stdout)   # Monday col shows 2.0000
            self.assertIn("10:00 PM - 12:00 AM", stdout)
            self.assertIn(f"{5.0:^12.4f}", stdout)   # Tuesday col shows 5.0000

            # Malformed rows reported (2 of them)
            self.assertIn("Error: skipped 2 malformed rows", stderr)

    def test_analyze_electric_usage_file_error(self):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            au.analyze_electric_usage("nope.csv")
        self.assertIn("Error:", err.getvalue())
        # Should not print a table if file couldn't be read
        self.assertNotIn("Average Energy Consumption", out.getvalue())


if __name__ == "__main__":
    unittest.main()
