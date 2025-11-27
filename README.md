# Clock - Timewarrior Wrapper

A Python wrapper around [timewarrior](https://timewarrior.net/) that provides:
- **12-hour time format** instead of 24-hour format
- **Improved readability** for time tracking
- **New `begin` command** for starting a timer with annotation in one step
- **Pass-through support** for all other timewarrior commands

## Installation

1. Clone or download the repository
2. Run the setup script to create a symlink:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Verify installation:
   ```bash
   clock help
   ```

## Usage

### Basic Commands

Display time tracking in 12-hour format:

```bash
clock day          # Display today's time tracking
clock week         # Display this week's time tracking
clock month        # Display this month's time tracking
clock summary      # Display summary with 12-hour times
```

### Begin Command

Start a timer with tags and optionally add an annotation in one step:

```bash
clock begin work "fixing bug"
clock begin project client feature "implementing login"
```

This command:
1. Starts a timewarrior timer with the specified tags
2. Adds the annotation to the current entry

### Pass-Through Commands

All other timewarrior commands are passed through directly:

```bash
clock start work                    # Start a timer
clock stop                          # Stop the current timer
clock continue                      # Continue the previous entry
clock show                          # Show configuration
clock help [command]                # Get help
clock cancel                        # Cancel current entry
clock delete @1                     # Delete entry @1
```

## Examples

### Tracking Your Day

```bash
# Start working on a project
clock begin work "morning standup"

# After standup, start new work
clock stop
clock begin work project-x "implementation phase"

# View your day's work
clock day
```

### Viewing Reports

```bash
# Today's activities in 12-hour format
clock day

# This week in 12-hour format
clock week

# This month in 12-hour format
clock month

# Summary of tracked time
clock summary
clock summary :week
clock summary :month
clock summary :yesterday
```

## Time Format

All time outputs are displayed in 12-hour format with AM/PM indicators:
- `06:30 AM` instead of `06:30`
- `02:15 PM` instead of `14:15`
- `11:59 PM` instead of `23:59`

## Requirements

- Python 3.6+
- timewarrior installed and configured

## Configuration

The wrapper reads all configuration from timewarrior directly. You can configure timewarrior as normal:

```bash
timew config
timew config [name] [value]
```

## Notes

- The wrapper is fully compatible with all timewarrior features
- All data is stored in the same timewarrior database
- You can freely mix using `clock` and `timew` commands
- Annotations, tags, and other features work identically

## Troubleshooting

If `clock` command is not found after installation:
- Ensure `~/.local/bin` is in your `$PATH`
- Or manually create a symlink: `ln -s /path/to/clock.py ~/.local/bin/clock`
- Or run directly: `python3 /path/to/clock.py <command>`
