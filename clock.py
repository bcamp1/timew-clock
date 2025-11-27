#!/usr/bin/env python3
"""
Clock - A wrapper around timewarrior (timew) with improved readability and 12-hour format.
"""

import subprocess
import sys
import re
from datetime import datetime
from typing import List


def convert_24h_to_12h(time_str: str) -> str:
    """Convert 24-hour format time to 12-hour format (only for times of day, not durations)."""
    try:
        # Try to parse as HH:MM:SS format first
        if time_str.count(':') == 2:
            parts = time_str.split(':')
            if len(parts) == 3:
                h = int(parts[0])
                m = int(parts[1])
                s = int(parts[2])
                # Only convert if this is a valid time of day (0-23 hours)
                # Don't convert durations which can exceed 23 hours
                if 0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60:
                    time_obj = datetime.strptime(time_str, '%H:%M:%S')
                    return time_obj.strftime('%I:%M:%S').lstrip('0') + time_obj.strftime('%p').lower()
        # Then try HH:MM format
        elif ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:
                h = int(parts[0])
                m = int(parts[1])
                # Only convert if this is a valid time of day (0-23 hours)
                if 0 <= h < 24 and 0 <= m < 60:
                    time_obj = datetime.strptime(time_str, '%H:%M')
                    return time_obj.strftime('%I:%M').lstrip('0') + time_obj.strftime('%p').lower()
    except (ValueError, AttributeError):
        pass
    return time_str


def convert_hour_to_12h(hour: int) -> str:
    """Convert a single hour (0-23) to 12-hour format (12a, 1a, ..., 12p, 11p)."""
    if hour == 0:
        return '12a'
    elif 1 <= hour < 12:
        return f'{hour}a'
    elif hour == 12:
        return '12p'
    else:
        return f'{hour - 12}p'


def convert_datetime_to_12h(dt_str: str) -> str:
    """Convert datetime string to 12-hour format."""
    # Try various datetime formats
    formats = [
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
    ]

    for fmt in formats:
        try:
            dt_obj = datetime.strptime(dt_str.replace('Z', '+0000').split('+')[0], fmt.replace('Z', ''))
            return dt_obj.strftime('%Y-%m-%d %I:%M %p')
        except ValueError:
            continue

    return dt_str


def run_timew_command(args: List[str]) -> str:
    """Execute a timewarrior command and return its output."""
    try:
        result = subprocess.run(['timew'] + args, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running timew: {e}"


def convert_hour_headers(output: str) -> str:
    """Convert hour headers (0-23) in day/week/month reports to 12-hour format."""
    lines = output.split('\n')
    result_lines = []

    for line in lines:
        # Check if this line looks like an hour header line
        # It should have multiple numbers separated by spaces at the beginning
        # Pattern: line starts with optional text then has "0    1    2    3 ..." etc
        if re.search(r'\s\d+\s+\d+\s+\d+\s+\d+\s+\d+', line):
            # This looks like a line with hour headers - convert them
            # Replace standalone hour numbers (0-23) with 12-hour format
            def replace_hour(match):
                hour = int(match.group(1))
                if 0 <= hour <= 23:
                    return convert_hour_to_12h(hour)
                return match.group(0)

            # Replace hours in the format: single or double digit numbers surrounded by word boundaries or spaces
            # But be careful not to replace numbers in other contexts
            converted_line = re.sub(r'\b(2[0-3]|[01]?[0-9])\b(?=\s{2,}|$|\s+[a-zA-Z])', replace_hour, line)
            result_lines.append(converted_line)
        else:
            result_lines.append(line)

    return '\n'.join(result_lines)


def convert_output_to_12h(output: str) -> str:
    """Convert 24-hour times in output to 12-hour format."""
    # First, convert hour headers (0-23) to 12-hour format
    output = convert_hour_headers(output)

    # Pattern for HH:MM:SS format first (hours 0-23)
    output = re.sub(r'\b([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])\b',
                    lambda m: convert_24h_to_12h(f"{m.group(1)}:{m.group(2)}:{m.group(3)}"),
                    output)

    # Also match single digit hours (0-9)
    output = re.sub(r'\b([0-9]):([0-5][0-9]):([0-5][0-9])\b',
                    lambda m: convert_24h_to_12h(f"{m.group(1)}:{m.group(2)}:{m.group(3)}"),
                    output)

    # Pattern for HH:MM times (that are not preceded by digits, not followed by seconds or AM/PM)
    # Hours 0-23, but not if preceded by another digit (to avoid matching :00 in 24:00:00)
    output = re.sub(r'(?<![0-9:])([01][0-9]|2[0-3]):([0-5][0-9])(?!:[0-5][0-9]|\s*[APap][Mm])',
                    lambda m: convert_24h_to_12h(f"{m.group(1)}:{m.group(2)}"),
                    output)

    # Single digit hours (0-9), but not if preceded by a digit or colon
    output = re.sub(r'(?<![0-9:])([0-9]):([0-5][0-9])(?!:[0-5][0-9]|\s*[APap][Mm])',
                    lambda m: convert_24h_to_12h(f"{m.group(1)}:{m.group(2)}"),
                    output)

    # Pattern for ISO datetime format
    output = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})',
                    lambda m: convert_datetime_to_12h(m.group(0)),
                    output)

    return output


def remove_day_column(text: str) -> str:
    """Remove the Day column from summary output and merge with Date column."""
    lines = text.split('\n')
    result_lines = []

    for line in lines:
        # Remove the "Day" column from header and separator lines
        if 'Date' in line and 'Day' in line:
            # Remove " Day" from the header line
            line = line.replace(' Day', '')
        elif line.startswith('---') and ' --- ' in line:
            # Remove the Day column separator ("--- ")
            # Replace "--- --- ---" with "--- ---" etc
            line = re.sub(r' --- +--- ', ' --- ', line)
        # For data rows with dates, the day is already there
        # Just clean up any duplicate spacing

        result_lines.append(line)

    return '\n'.join(result_lines)


def format_dates_in_summary(text: str) -> str:
    """Format dates in summary output to mm/dd format."""
    # Match dates in format YYYY-MM-DD and convert to MM/DD
    text = re.sub(r'\b(\d{4})-(\d{2})-(\d{2})\b',
                  lambda m: f"{m.group(2)}/{m.group(3)}",
                  text)
    return text


def remove_seconds_from_times(text: str) -> str:
    """Remove seconds from time displays (HH:MM:SSam/pm -> HH:MMam/pm)."""
    # Match times in format HH:MM:SSam/pm and replace with HH:MMam/pm
    text = re.sub(r'\b(\d{1,2}):(\d{2}):\d{2}([ap]m)\b',
                  r'\1:\2\3',
                  text)
    return text


def replace_timew_with_clock(text: str) -> str:
    """Replace 'timew' command references with 'clock' in help text."""
    # Replace "timew <command>" with "clock <command>" at the start of lines
    text = re.sub(r'^       timew ', '       clock ', text, flags=re.MULTILINE)
    # Also replace standalone "timew" at the start of usage lines
    text = re.sub(r'^Usage: timew', 'Usage: clock', text, flags=re.MULTILINE)
    return text


def print_result(result: str):
    """Print result and exit cleanly."""
    print(result, end='')
    sys.exit(0)


def main():
    """Main entry point for clock command."""
    if len(sys.argv) < 2:
        # No command, show summary instead of help (more useful than timew's default)
        output = run_timew_command(['summary'])
        output = convert_output_to_12h(output)
        # Remove seconds for cleaner summary display
        output = remove_seconds_from_times(output)
        # Format dates as mm/dd
        output = format_dates_in_summary(output)
        # Remove Day column and merge with Date
        output = remove_day_column(output)
        print_result(output)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == 'help':
        # Show help with clock instead of timew
        output = run_timew_command(['help'] + args)
        output = replace_timew_with_clock(output)
        # Add info about the new 'begin' command
        if len(args) == 0:  # Only add to main help, not subcommand help
            output += "\n       clock begin <tags> \"<annotation>\"  (new: start timer with annotation)"
        print_result(output)

    elif command == 'day':
        output = run_timew_command(['day'] + args)
        print_result(convert_output_to_12h(output))

    elif command == 'week':
        output = run_timew_command(['week'] + args)
        print_result(convert_output_to_12h(output))

    elif command == 'month':
        output = run_timew_command(['month'] + args)
        print_result(convert_output_to_12h(output))

    elif command == 'summary':
        output = run_timew_command(['summary'] + args)
        output = convert_output_to_12h(output)
        # Remove seconds for cleaner summary display
        output = remove_seconds_from_times(output)
        # Format dates as mm/dd
        output = format_dates_in_summary(output)
        # Remove Day column and merge with Date
        output = remove_day_column(output)
        print_result(output)

    elif command == 'begin':
        # Parse: clock begin <tags...> "<annotation>"
        # The annotation should be quoted (with double quotes)
        if len(args) == 0:
            print_result("Error: begin requires at least tags. Usage: clock begin <tags> \"<annotation>\"")

        # Find the last double-quoted argument
        tags = []
        annotation = ""

        for i, arg in enumerate(args):
            if arg.startswith('"') and arg.endswith('"'):
                # Found a fully quoted annotation
                annotation = arg[1:-1]  # Remove quotes
                break
            elif arg.startswith('"'):
                # Found start of quoted annotation - collect all args until closing quote
                annotation_parts = []
                for j in range(i, len(args)):
                    part = args[j]
                    annotation_parts.append(part.rstrip('"'))
                    if part.endswith('"'):
                        break
                annotation = ' '.join(annotation_parts)
                annotation = annotation[1:-1] if annotation.startswith('"') else annotation
                break
            else:
                tags.append(arg)

        # Start the timer
        result = run_timew_command(['start'] + tags)
        output = convert_output_to_12h(result)

        # Add annotation if provided
        if annotation:
            ann_result = run_timew_command(['ann', annotation])
            output += "\n" + ann_result

        print_result(output)

    else:
        # Pass through to timew
        output = run_timew_command([command] + args)
        print_result(convert_output_to_12h(output))


if __name__ == '__main__':
    main()
