import csv
from datetime import datetime
import sys
import os
from typing import Dict, List, Tuple, Optional, TextIO


DAYS_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TIME_WINDOWS = list(range(0, 24, 2))
DATE_FORMAT = "%m/%d/%Y"
TIME_FORMAT = "%I:%M %p"
HOUR_FORMAT = "%H"


class ElectricityUsageAnalyzer:
    """
    Analyzes electricity usage data from 15-minute interval readings.
    Calculates average consumption for 2-hour windows for each day of the week.
    """

    def __init__(self):
        self.weekly_usage = {
            day: {hour: [] for hour in TIME_WINDOWS}
            for day in range(7)
        }
        self.malformed_rows = 0

    def process_row(self, row: Dict[str, str]) -> Optional[Tuple[int, int, float]]:
        """
        Process a single row of CSV data and extract relevant information.

        Args:
            row: A dictionary representing a row of CSV data

        Returns:
            A tuple of (day_of_week, time_window_start, consumption) if successful,
            None if the row is malformed
        """
        try:
            date = datetime.strptime(
                row["Date"] + " " + row["Start Time"],
                DATE_FORMAT + " " + TIME_FORMAT,
            )
            day_of_week = date.weekday()
            hour = date.hour
            time_window_start = (hour // 2) * 2  # Group into 2-hour windows
            consumption = float(row["Consumption"])
            return (day_of_week, time_window_start, consumption)
        except (ValueError, KeyError):
            self.malformed_rows += 1
            return None

    def process_csv_data(self, csv_data: List[Dict[str, str]]) -> None:
        """
        Process CSV data and populate the weekly_usage data structure.

        Args:
            csv_data: A list of dictionaries representing CSV rows
        """
        for row in csv_data:
            if result := self.process_row(row):
                day_of_week, time_window_start, consumption = result
                self.weekly_usage[day_of_week][time_window_start].append(consumption)

    def calculate_averages(self) -> Dict[int, Dict[int, float]]:
        """
        Calculate average consumption for each day and time window.

        Returns:
            A dictionary with average consumption values
        """
        averages = {day: {} for day in range(7)}

        for day, windows in self.weekly_usage.items():
            for window, values in windows.items():
                if values:
                    avg = sum(values) / len(values)
                    averages[day][window] = avg
                else:
                    # If there's no data for a window, average is 0
                    averages[day][window] = 0.0

        return averages

    def get_malformed_rows_count(self) -> int:
        """Return the count of malformed rows encountered during processing."""
        return self.malformed_rows


def read_csv_file(file_path: str) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """
    Read a CSV file and return its data as a list of dictionaries.

    This helper handles input files that might include a UTF-8 BOM on the first
    line. Opening with ``utf-8-sig`` will strip the BOM so that ``csv.DictReader``
    can parse the quoted header correctly.

    Args:
        file_path: Path to the CSV file

    Returns:
        A tuple of (csv_data, error_message) where error_message is None if successful
    """
    try:
        # newline='' recommended by csv module documentation to prevent newline
        # translation issues on all platforms.
        with open(file_path, mode="r", encoding="utf-8-sig", newline="") as csvfile:
            csv_data = list(csv.DictReader(csvfile))
            return csv_data, None
    except IOError as e:
        return [], str(e)


def format_time_window_label(hour: int) -> str:
    """
    Format a time window label for a given starting hour.

    Args:
        hour: The starting hour of the time window (0, 2, 4, ..., 22)

    Returns:
        A formatted string representing the time window (e.g., "12:00 AM - 02:00 AM")
    """
    start_time_obj = datetime.strptime(str(hour), HOUR_FORMAT)
    end_time_obj = datetime.strptime(str((hour + 2) % 24), HOUR_FORMAT)

    # Handle the midnight case for the label end time
    if hour == 22:
        end_time_label = "12:00 AM"
    else:
        end_time_label = end_time_obj.strftime(TIME_FORMAT).lstrip("0")

    time_label = (
        f"{start_time_obj.strftime(TIME_FORMAT).lstrip('0')} - {end_time_label}"
    )

    return time_label


def format_output_table(averages: Dict[int, Dict[int, float]]) -> str:
    """
    Format the average consumption data as a table string.

    Args:
        averages: A dictionary with average consumption values

    Returns:
        A formatted string representing the table
    """
    header = f"{'Time Window':<22}" + "".join([f"{day:^12}" for day in DAYS_OF_WEEK])
    output_lines = [
        "\nAverage Energy Consumption (kWh) by Time and Day of Week\n",
        header,
        "-" * len(header),
    ]

    for hour in TIME_WINDOWS:
        time_label = format_time_window_label(hour)
        row_str = f"{time_label:<22}"
        for day_index in range(7):
            avg_value = averages[day_index].get(hour, 0.0)
            row_str += f"{avg_value:^12.4f}"
        output_lines.append(row_str)

    return "\n".join(output_lines)


def analyze_electric_usage(file_path: str) -> None:
    """
    Parses a 15-minute interval electricity usage CSV file, calculates
    the average consumption for 2-hour windows for each day of the week,
    and prints the results.

    Args:
        file_path: The path to the CSV file.
    """
    csv_data, error = read_csv_file(file_path)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        return

    analyzer = ElectricityUsageAnalyzer()
    analyzer.process_csv_data(csv_data)

    malformed_count = analyzer.get_malformed_rows_count()
    if malformed_count > 0:
        print(f"Error: skipped {malformed_count} malformed rows", file=sys.stderr)

    averages = analyzer.calculate_averages()
    print(format_output_table(averages))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        script = os.path.basename(sys.argv[0])
        print(f"Usage: python {script} <path_to_csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]
    analyze_electric_usage(csv_file)
