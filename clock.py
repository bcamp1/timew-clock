#!/usr/bin/env python3
"""
Clock - A wrapper around timewarrior (timew) with improved readability and 12-hour format.
"""

import subprocess
import sys
import re
from datetime import datetime
from typing import List

__version__ = "1.0.0"


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


def convert_summary_to_12h(output: str) -> str:
    """Convert Start and End times in summary output to 12-hour format.

    Only converts the Start and End columns, preserving Time and Total columns as-is
    since they are durations, not times of day.

    Handles both completed and ongoing tasks:
    - Completed: HH:MM:SS HH:MM:SS (has end time)
    - Ongoing: HH:MM:SS - (has dash instead of end time)
    """
    lines = output.split('\n')
    result_lines = []

    for line in lines:
        # Skip empty lines and header/separator lines
        if not line.strip() or line.startswith('---') or 'Tags' in line:
            result_lines.append(line)
            continue

        # For continuation rows (indented, without week), look for start/end times
        if not re.match(r'^W\d+', line) and line.strip():
            # Check for ongoing task (HH:MM:SS -)
            match_ongoing = re.search(r'(\d{1,2}:\d{2}:\d{2})\s+-', line)
            if match_ongoing:
                start_time = match_ongoing.group(1)
                start_12h = convert_24h_to_12h(start_time)
                # Replace start time, keep the dash
                line = line[:match_ongoing.start()] + f"{start_12h} -" + line[match_ongoing.end():]
            else:
                # Check for completed task (HH:MM:SS HH:MM:SS)
                match = re.search(r'(\d{1,2}:\d{2}:\d{2})\s+(\d{1,2}:\d{2}:\d{2})', line)
                if match:
                    start_time = match.group(1)
                    end_time = match.group(2)
                    start_12h = convert_24h_to_12h(start_time)
                    end_12h = convert_24h_to_12h(end_time)
                    # Replace in line
                    line = line[:match.start()] + f"{start_12h} {end_12h}" + line[match.end():]
            result_lines.append(line)
            continue

        # Match primary rows: W## YYYY-MM-DD Day TAGS START END TIME [TOTAL]
        # Check for ongoing task (HH:MM:SS -)
        match_ongoing = re.search(r'(\d{1,2}:\d{2}:\d{2})\s+-', line)
        if match_ongoing:
            start_time = match_ongoing.group(1)
            start_12h = convert_24h_to_12h(start_time)
            # Replace start time, keep the dash
            converted_line = line[:match_ongoing.start()] + f"{start_12h} -" + line[match_ongoing.end():]
            result_lines.append(converted_line)
            continue

        # Check for completed task (HH:MM:SS HH:MM:SS)
        match = re.search(r'(\d{1,2}:\d{2}:\d{2})\s+(\d{1,2}:\d{2}:\d{2})', line)
        if match:
            start_time = match.group(1)
            end_time = match.group(2)

            # Convert start and end times to 12-hour format
            start_12h = convert_24h_to_12h(start_time)
            end_12h = convert_24h_to_12h(end_time)

            # Replace in line
            converted_line = line[:match.start()] + f"{start_12h} {end_12h}" + line[match.end():]
            result_lines.append(converted_line)
        else:
            result_lines.append(line)

    return '\n'.join(result_lines)


def format_duration(duration_str: str) -> str:
    """Convert duration from HH:MM:SS format to human-readable format (e.g., 1h32m or 45m)."""
    try:
        parts = duration_str.split(':')
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            # Ignore seconds
            if hours == 0:
                return f"{minutes}m" if minutes > 0 else "0m"
            elif minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h{minutes}m"
    except (ValueError, IndexError):
        pass
    return duration_str


def format_summary_durations(text: str) -> str:
    """Convert duration columns (Time and Total) to human-readable format.

    Converts HH:MM:SS to Xh, Ym, or XhYm format.
    """
    lines = text.split('\n')
    result_lines = []

    for line in lines:
        # Skip empty lines and header/separator lines
        if not line.strip() or line.startswith('---') or 'Tags' in line:
            result_lines.append(line)
            continue

        # For continuation rows (indented, without week), process any durations
        if not re.match(r'^W\d+', line) and line.strip():
            # Continuation rows might have start/end times converted already (from convert_summary_to_12h)
            # Find all HH:MM:SS or Xh/Yam patterns and convert remaining durations
            # We need to be careful not to convert times with am/pm (those are start/end times)

            # Convert all remaining H:MM:SS or HH:MM:SS patterns that don't have am/pm
            def replace_duration(match):
                full_match = match.group(0)
                # Check if this time is followed by am/pm (it's a converted time, not a duration)
                if re.search(r'[ap]m\s', line[match.end():match.end()+3]):
                    return full_match
                duration_str = full_match
                return format_duration(duration_str)

            line = re.sub(r'\d{1,2}:\d{2}:\d{2}', replace_duration, line)
            result_lines.append(line)
            continue

        # For primary rows, find and convert all durations
        # After conversion by convert_summary_to_12h(), times look like "10:23:04pm"
        # Durations still look like "1:00:54"
        # We need to convert the durations but not touch the times

        # Convert all HH:MM:SS that are NOT followed by am/pm
        def replace_duration(match):
            full_match = match.group(0)
            # Check if followed by am/pm (it's a time, not duration)
            pos = match.end()
            if pos < len(line) and line[pos:pos+1] in ['a', 'p']:
                # This is likely "HH:MM:SS" followed by am/pm
                return full_match
            return format_duration(full_match)

        line = re.sub(r'\d{1,2}:\d{2}:\d{2}', replace_duration, line)
        result_lines.append(line)

    return '\n'.join(result_lines)


def convert_total_to_duration(text: str) -> str:
    """Convert Total column from time format to duration format (e.g., 6:53am -> 6h53m).

    This function handles the case where Total is in 12-hour format (from incorrect
    conversion of durations) and converts to human-readable format.
    """
    lines = text.split('\n')
    result_lines = []

    for line in lines:
        # Skip header and separator lines
        if not line.strip() or line.startswith('---') or 'Tags' in line:
            result_lines.append(line)
            continue

        # Match times in the Total column (last column with am/pm)
        # Replace the last occurrence of HH:MM[ap]m with duration format
        # Use a negative lookbehind to ensure we're at the end or followed by spaces/end
        match = re.search(r'(\d{1,2}):(\d{2})([ap]m)(?=\s*$)', line)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))

            # Convert to duration format
            if minutes == 0:
                duration = f"{hours}h"
            else:
                duration = f"{hours}h{minutes:02d}m"

            # Replace in the line
            line = line[:match.start()] + duration + line[match.end():]

        result_lines.append(line)

    return '\n'.join(result_lines)


def align_summary_columns(text: str, show_annotations: bool = False) -> str:
    """Right-align time columns so am/pm values line up.

    Args:
        text: The summary output text to align
        show_annotations: If True, label the Tags column as "Tags / Reason"
    """
    lines = text.split('\n')

    # First pass: find max widths for all columns
    max_widths = {'wk': 0, 'date': 0, 'tags': 0, 'start': 0, 'end': 0, 'time': 0, 'total': 0}

    for line in lines:
        # Skip empty lines and header/separator lines
        if not line.strip() or line.startswith('---') or 'Tags' in line:
            continue

        # Match primary rows (with week/date)
        if re.match(r'^W\d+', line):
            # Match: Wk Date Tags Start(time) End(time or dash) Time(duration) [Total(duration)]
            match = re.match(r'^(W\d+)\s+(\d{2}/\d{2}\s+\w{3})\s+(.+?)(\d{1,2}:\d{2}[ap]m)\s+(-|\d{1,2}:\d{2}[ap]m)\s+([\dh]+m?|\d+m)(?:\s+([\dh]+m?|\d+m))?', line)
            if match:
                max_widths['wk'] = max(max_widths['wk'], len(match.group(1)))
                max_widths['date'] = max(max_widths['date'], len(match.group(2)))
                max_widths['tags'] = max(max_widths['tags'], len(match.group(3).rstrip()))
                max_widths['start'] = max(max_widths['start'], len(match.group(4)))
                max_widths['end'] = max(max_widths['end'], len(match.group(5)))
                max_widths['time'] = max(max_widths['time'], len(match.group(6)))
                if match.group(7):
                    max_widths['total'] = max(max_widths['total'], len(match.group(7)))
        else:
            # Match continuation rows (no week/date)
            # Match: indent Tags Start(time) End(time or dash) Time(duration) [Total(duration)]
            match = re.match(r'^(\s+)(.+?)(\d{1,2}:\d{2}[ap]m)\s+(-|\d{1,2}:\d{2}[ap]m)\s+([\dh]+m?|\d+m)(?:\s+([\dh]+m?|\d+m))?', line)
            if match:
                max_widths['tags'] = max(max_widths['tags'], len(match.group(2).rstrip()))
                max_widths['start'] = max(max_widths['start'], len(match.group(3)))
                max_widths['end'] = max(max_widths['end'], len(match.group(4)))
                max_widths['time'] = max(max_widths['time'], len(match.group(5)))
                if match.group(6):
                    max_widths['total'] = max(max_widths['total'], len(match.group(6)))

    # Second pass: format lines with proper alignment
    result_lines = []
    for line in lines:
        # Handle empty lines
        if not line.strip():
            result_lines.append(line)
            continue

        # Handle header line (contains "Tags")
        if 'Tags' in line:
            # Rebuild header with proper column widths (no vertical dividers, just spacing to match separator)
            tags_label = 'Tags / Reason' if show_annotations else 'Tags'
            header = (
                f"{'Wk':<{max_widths['wk']}}   "
                f"{'Date':<{max_widths['date']}}   "
                f"{tags_label:<{max_widths['tags']}}   "
                f"{'Start':>{max_widths['start']}}   "
                f"{'End':>{max_widths['end']}}   "
                f"{'Time':>{max_widths['time']}}   "
                f"{'Total':>{max_widths['total']}}"
            )
            result_lines.append(header)
            continue

        # Handle separator line (dashes)
        if line.startswith('---') or line.startswith('───'):
            # Rebuild separator with proper column widths using box-drawing characters
            separator = (
                f"{'─' * max_widths['wk']}─┼─"
                f"{'─' * max_widths['date']}─┼─"
                f"{'─' * max_widths['tags']}─┼─"
                f"{'─' * max_widths['start']}─┼─"
                f"{'─' * max_widths['end']}─┼─"
                f"{'─' * max_widths['time']}─┼─"
                f"{'─' * max_widths['total']}"
            )
            result_lines.append(separator)
            continue

        # Match and format primary rows
        if re.match(r'^W\d+', line):
            match = re.match(r'^(W\d+)\s+(\d{2}/\d{2}\s+\w{3})\s+(.+?)(\d{1,2}:\d{2}[ap]m)\s+(-|\d{1,2}:\d{2}[ap]m)\s+([\dh]+m?|\d+m)(?:\s+([\dh]+m?|\d+m))?', line)
            if match:
                wk = match.group(1)
                date = match.group(2)
                tags = match.group(3).rstrip()
                start = match.group(4)
                end = match.group(5)
                time = match.group(6)
                total = match.group(7) or ''

                formatted = (
                    f"{wk:<{max_widths['wk']}} │ "
                    f"{date:<{max_widths['date']}} │ "
                    f"{tags:<{max_widths['tags']}} │ "
                    f"{start:>{max_widths['start']}} │ "
                    f"{end:>{max_widths['end']}} │ "
                    f"{time:>{max_widths['time']}} │ "
                    f"{total:>{max_widths['total']}}"
                )
                result_lines.append(formatted)
            else:
                result_lines.append(line)
        else:
            # Match and format continuation rows
            match = re.match(r'^(\s+)(.+?)(\d{1,2}:\d{2}[ap]m)\s+(-|\d{1,2}:\d{2}[ap]m)\s+([\dh]+m?|\d+m)(?:\s+([\dh]+m?|\d+m))?', line)
            if match:
                tags = match.group(2).rstrip()
                start = match.group(3)
                end = match.group(4)
                time = match.group(5)
                total = match.group(6) or ''

                # Calculate indent to align with data columns with proper vertical borders
                # Format: [Wk spaces] │ [Date spaces] │
                indent = (
                    f"{' ' * max_widths['wk']} │ "
                    f"{' ' * max_widths['date']} │ "
                )
                formatted = (
                    f"{indent}"
                    f"{tags:<{max_widths['tags']}} │ "
                    f"{start:>{max_widths['start']}} │ "
                    f"{end:>{max_widths['end']}} │ "
                    f"{time:>{max_widths['time']}} │ "
                    f"{total:>{max_widths['total']}}"
                )
                result_lines.append(formatted)
            else:
                result_lines.append(line)

    return '\n'.join(result_lines)


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


def label_grand_total(text: str) -> str:
    """Add 'Grand Total:' label to the final summary total line."""
    lines = text.split('\n')
    result_lines = []

    # Find the table width by looking for the separator line
    table_width = 0
    for line in lines:
        if re.match(r'^─+┼', line):  # Separator line starts with dashes and intersection
            table_width = len(line)
            break

    for i, line in enumerate(lines):
        # Look for the grand total line: mostly whitespace followed by a duration
        # Pattern: whitespace, then h/m duration at the end of the line
        if re.match(r'^\s+[\dh]+m?\s*$', line):
            # This is likely the grand total line
            # Get the duration value
            duration = line.strip()
            # Replace with labeled version, right-aligned to the table width
            label = f"Grand Total: {duration}"
            result_lines.append(f"{label:>{table_width}}")
        else:
            result_lines.append(line)

    return '\n'.join(result_lines)


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
        # Convert Start and End times to 12-hour format (not Time/Total which are durations)
        output = convert_summary_to_12h(output)
        # Remove seconds from time display
        output = remove_seconds_from_times(output)
        # Format duration columns to human-readable format
        output = format_summary_durations(output)
        # Format dates as mm/dd
        output = format_dates_in_summary(output)
        # Remove Day column and merge with Date
        output = remove_day_column(output)
        # Align columns
        output = align_summary_columns(output)
        # Label the grand total
        output = label_grand_total(output)
        print_result(output)

    command = sys.argv[1]
    args = sys.argv[2:]

    # Support shorthand aliases
    if command == 's':
        command = 'summary'

    if command == 'help':
        # Show help with clock instead of timew
        output = run_timew_command(['help'] + args)
        output = replace_timew_with_clock(output)
        # Add info about the new 'begin' command
        if len(args) == 0:  # Only add to main help, not subcommand help
            output += "\n       clock begin <tags> \"<annotation>\"  (new: start timer with annotation)"
        print_result(output)

    elif command == 'version':
        print_result(f"clock {__version__}\n")

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
        # Convert Start and End times to 12-hour format (not Time/Total which are durations)
        output = convert_summary_to_12h(output)
        # Remove seconds from time display
        output = remove_seconds_from_times(output)
        # Format duration columns to human-readable format
        output = format_summary_durations(output)
        # Format dates as mm/dd
        output = format_dates_in_summary(output)
        # Remove Day column and merge with Date
        output = remove_day_column(output)
        # Align columns (check if annotations are being shown)
        show_ann = ':ann' in args
        output = align_summary_columns(output, show_annotations=show_ann)
        # Label the grand total
        output = label_grand_total(output)
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
