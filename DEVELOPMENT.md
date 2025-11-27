# Clock Development Guide

This document provides an overview of the Clock project architecture, implementation details, and development notes for future contributors and AI assistants.

## Project Overview

**Clock** is a Python wrapper around [Timewarrior](https://timewarrior.net/) (the `timew` CLI tool) that provides:
- **12-hour time format** display instead of 24-hour (with lowercase am/pm: 9:46am, not 9:46 AM)
- **Improved readability** with better formatting and alignment
- **New `begin` command** to start timers with tags and annotations in one step
- **Human-readable durations** (1h32m instead of 1:32:00)
- **Professional table styling** with box-drawing characters
- **Pass-through support** for all timewarrior commands

## Architecture

### Core File: `clock.py`

The main script (~635 lines) is the complete wrapper implementation. Current version: **1.0.0**

#### Entry Point: `main()`
- Handles command routing
- No arguments: shows `summary` instead of help (more useful than timew default)
- Supports command aliases (e.g., `s` → `summary`)
- Handles special commands: `version`, `help`, `day`, `week`, `month`, `summary`, `begin`
- Passes unknown commands through to timew

#### Processing Pipeline

The summary command applies transformations in this specific order:

```
timew summary [args]
    ↓
convert_summary_to_12h()      # Convert Start/End times (not durations)
    ↓
remove_seconds_from_times()   # HH:MM:SSam → HH:MMam
    ↓
format_summary_durations()    # HH:MM:SS → 1h32m format
    ↓
format_dates_in_summary()     # YYYY-MM-DD → MM/DD
    ↓
remove_day_column()           # Merge Day into Date column
    ↓
align_summary_columns()       # Right-align columns, add borders
```

### Key Functions

#### Time Conversion Functions

**`convert_24h_to_12h(time_str: str) -> str`**
- Converts times in 24-hour format to 12-hour format
- Validates hours (0-23) to distinguish times of day from durations
- Handles both HH:MM:SS and HH:MM formats
- Returns lowercase am/pm (9:46am not 9:46 AM)

**`convert_hour_to_12h(hour: int) -> str`**
- Converts single hour numbers (0-23) to 12-hour format labels
- 0→"12a", 1-11→"1a"-"11a", 12→"12p", 13-23→"1p"-"11p"
- Used for header conversion in day/week/month reports

**`convert_summary_to_12h(output: str) -> str`**
- Specialized converter for summary output
- **Key difference**: Only converts Start/End times, NOT Time/Total (which are durations)
- Handles both completed tasks (HH:MM:SS HH:MM:SS) and ongoing tasks (HH:MM:SS -)
- Uses order-dependent regex matching: checks for ongoing tasks first (with dash), then completed tasks
- Preserves duration format in Time and Total columns

**`convert_output_to_12h(output: str) -> str`**
- General-purpose converter for day/week/month reports
- Converts hour headers AND time values
- Used for pass-through commands that don't need duration formatting

#### Duration Functions

**`format_duration(duration_str: str) -> str`**
- Converts HH:MM:SS format to human-readable (1h32m, 54m, etc.)
- Ignores seconds
- Returns "0m" if empty

**`format_summary_durations(text: str) -> str`**
- Applies duration formatting to Time and Total columns
- Carefully avoids converting times with am/pm suffix (which are start/end times)
- Uses lookahead to detect am/pm following times

#### Column Alignment

**`align_summary_columns(text: str, show_annotations: bool = False) -> str`**
- **Two-pass algorithm**:
  1. **Pass 1**: Scan all lines to calculate max column widths (right-aligned for times, left for text)
  2. **Pass 2**: Rebuild all lines with consistent widths and box-drawing characters
- Rebuilds header row dynamically with proper column labels
- Rebuilds separator row with box-drawing characters (─, ┼, │)
- Supports optional Total column
- Supports annotation display mode (labels Tags column as "Tags / Reason" when `:ann` option is used)
- Maintains proper vertical borders (│) between all columns

#### Formatting Functions

**`remove_seconds_from_times(text: str) -> str`**
- Strips seconds from time display (HH:MM:SSam/pm → HH:MMam/pm)

**`format_dates_in_summary(text: str) -> str`**
- Converts YYYY-MM-DD dates to MM/DD format

**`remove_day_column(text: str) -> str`**
- Removes the separate Day column from output
- Merges day information into Date column (e.g., "11/26 Wed")

**`replace_timew_with_clock(text: str) -> str`**
- Used in help output to replace "timew" with "clock" in command references

#### Utility Functions

**`run_timew_command(args: List[str]) -> str`**
- Executes timew with given arguments
- Returns stdout + stderr combined

**`print_result(result: str)`**
- Prints result and exits cleanly

## Technical Patterns & Decisions

### 1. Distinguishing Times from Durations
**Problem**: Both times of day and durations look like HH:MM:SS, but need different handling.

**Solution**: Use hour value validation
- Times of day: hours must be 0-23
- Durations: can exceed 23 hours
- This validation prevents incorrect conversion of durations to 12-hour format

### 2. Order-Dependent Regex Matching
**Problem**: Ongoing tasks (with dash) can be confused with start/end time pairs.

**Solution**: Check for ongoing tasks FIRST before checking for completed tasks
```python
# Check ongoing task pattern first (HH:MM:SS -)
if re.search(r'(\d{1,2}:\d{2}:\d{2})\s+-', line):
    # Handle dash case
# Then check completed task pattern (HH:MM:SS HH:MM:SS)
elif re.search(r'(\d{1,2}:\d{2}:\d{2})\s+(\d{1,2}:\d{2}:\d{2})', line):
    # Handle completed case
```

### 3. Two-Pass Column Alignment
**Problem**: Headers/separators don't match dynamic column widths.

**Solution**: Two-pass algorithm
- Pass 1: Calculate max width for each column by scanning all data rows
- Pass 2: Rebuild all rows (including headers/separators) using calculated widths

### 4. Regex Patterns for Hours
**Important**: Use `\d{1,2}` not `\d{2}` to match both single-digit (9:00) and double-digit (09:00) hours.

### 5. Time Lookahead for Duration Detection
**Problem**: After conversion, times look like "10:23:04pm" and durations look like "1:00:54". Can be confused.

**Solution**: Check for am/pm suffix to identify converted times
```python
# Check if followed by am/pm (it's a time, not duration)
if line[match.end():match.end()+1] in ['a', 'p']:
    return full_match  # Don't format
return format_duration(full_match)  # Format as duration
```

## Commands Implemented

### Standard Commands (with enhancements)
- **`clock day [args]`** - Shows day report in 12-hour format
- **`clock week [args]`** - Shows week report in 12-hour format
- **`clock month [args]`** - Shows month report in 12-hour format
- **`clock summary [args]`** - Shows formatted summary with all enhancements (12h, human durations, aligned columns)
- **`clock help [topic]`** - Shows help with "timew" replaced with "clock"
- **`clock version`** - Shows current version (1.0.0)

### New Commands
- **`clock begin <tags> "<annotation>"`** - Starts timer with tags and adds annotation in one command
  - Internally: `timew start <tags>` followed by `timew ann "<annotation>"`

### Shorthand Aliases
- **`clock s <args>`** → `clock summary <args>`
- (Can be extended as needed)

### Default Behavior
- **`clock`** (no args) → shows `clock summary` instead of help

## Known Issues & Fixes

### Issue 1: Duration vs Time Confusion
**Symptom**: Total column shows "6:53am" instead of duration format
**Root Cause**: Single conversion function treated all HH:MM:SS as times
**Fix**: Created `convert_summary_to_12h()` that only converts Start/End times, not Time/Total columns

### Issue 2: Ongoing Task Handling
**Symptom**: Dash in End column (ongoing task) treated as second time
**Root Cause**: Regex pattern `(\d{2}:\d{2}:\d{2})\s+(\d{2}:\d{2}:\d{2})` didn't account for dashes
**Fix**: Added order-dependent check: match ongoing tasks (with dash) before completed tasks

### Issue 3: Single-Digit Hours Not Matched
**Symptom**: Hours like "9:40:42" weren't converted
**Root Cause**: Regex patterns used `\d{2}` expecting two digits
**Fix**: Changed all hour patterns to `\d{1,2}` to match 1-2 digit hours

### Issue 4: Header/Separator Misalignment
**Symptom**: Column headers and separators didn't align with data rows
**Root Cause**: Static headers vs dynamic data column widths
**Fix**: Implemented two-pass algorithm that rebuilds headers/separators dynamically

### Issue 5: Missing Vertical Borders in Continuation Rows
**Symptom**: Gaps appeared in table structure for multi-line entries
**Root Cause**: Indent calculation used plain spaces without vertical borders
**Fix**: Changed indent format to include vertical borders: `f"{' ' * wk} │ {' ' * date} │ "`

### Issue 6: Gap Between Time and Total Columns
**Symptom**: Missing vertical border between Time and Total columns
**Root Cause**: Conditional check `if total:` only added border when total had value
**Fix**: Always include ` │ ` between Time and Total, regardless of total value

## Output Examples

### Summary Output (formatted)
```
Wk     │ Date     │ Tags              │    Start │      End │     Time │    Total
───────┼──────────┼───────────────────┼──────────┼──────────┼──────────┼─────────
W47    │ 11/18    │ project work      │  9:23am  │  1:15pm  │     3h52m │
       │          │ break              │  1:45pm  │  3:30pm  │    1h45m │
W48    │ 11/26    │ meeting urgent    │  8:00am  │  9:30am  │    1h30m │
       │          │ coding             │ 10:00am  │    -     │     1h15m │
```

### Version Output
```
clock 1.0.0
```

## Testing

### Manual Testing Checklist
```bash
# Basic commands
python3 clock.py                          # Should show summary
python3 clock.py version                  # Should show "clock 1.0.0"
python3 clock.py help                     # Should show help with "clock" instead of "timew"
python3 clock.py s :month                 # Shorthand alias for summary

# Full commands
python3 clock.py day                      # Day report in 12h format
python3 clock.py week                     # Week report in 12h format
python3 clock.py month                    # Month report in 12h format
python3 clock.py summary :month           # Summary with all enhancements

# New commands
python3 clock.py begin mytag "doing work" # Start with annotation

# Pass-through commands
python3 clock.py report                   # Any timew command works
```

### Development Testing Notes
- Created test files in `/tmp/` (debug_pipeline.py, test_conversion.py, clock_day.txt)
- Use these for isolated testing of specific functions
- Can be safely deleted after debugging

## Version History

- **1.0.0** (Latest)
  - Initial feature-complete version
  - All core commands implemented (day, week, month, summary)
  - 12-hour time format with human-readable durations
  - Professional table styling with box-drawing characters
  - Version command added
  - Previous development work:
    - Fancy border styling (box-drawing characters)
    - Annotation labeling (Tags / Reason when :ann option used)
    - Shorthand aliases (s → summary)
    - Column alignment with two-pass algorithm
    - Complete formatting pipeline for summary output

## Future Enhancement Ideas

1. **Configuration File**: ~/.clockrc for custom formatting preferences
2. **Color Output**: ANSI colors for different task types
3. **Additional Aliases**: More shorthand commands
4. **Export Formats**: JSON, CSV export capabilities
5. **Analytics**: Summary statistics (total time, most productive day, etc.)
6. **Custom Reports**: Allow users to define custom report formats

## Setup & Installation

```bash
# Run setup script to create symlink
./setup.sh

# Or manually create symlink
ln -s $(pwd)/clock.py ~/.local/bin/clock
```

## Key Files

- **clock.py** - Main wrapper script (executable, ~635 lines)
- **setup.sh** - Installation helper script
- **CLAUDE.md** - User project instructions
- **DEVELOPMENT.md** - This file (development guide for future work)
- **.gitignore** - Standard Python excludes

## Important Notes for Future Development

1. **Always increment version** in `__version__` variable when making changes
2. **Test the full pipeline** - changes in one function can affect later transformations
3. **Be careful with regex patterns** - use `\d{1,2}` for hours, not `\d{2}`
4. **Order matters** - the transformation pipeline order is critical (don't rearrange)
5. **Two-pass alignment** - if modifying column handling, remember the two-pass algorithm
6. **Box-drawing characters** - use proper Unicode characters (│, ─, ┼) for borders
7. **Distinction is key** - always remember: times of day (0-23) vs durations (can exceed 23)

## Debugging Tips

1. **Isolate transformations**: Create a test script applying one function at a time
2. **Print intermediate states**: Check output after each transformation step
3. **Use repr()**: Print with repr() to see whitespace clearly
4. **Test edge cases**: Ongoing tasks (with dash), multi-line entries, empty columns
5. **Regex testing**: Use regex101.com to test patterns with real timewarrior output

---

Last updated: 2025-11-26
Development history: Complete implementation from scratch with iterative refinement based on UX feedback.
