# Clock

A wrapper around [Timewarrior](https://timewarrior.net/) that displays time in 12-hour format with human-readable durations and properly aligned columns.

## Installation

```bash
git clone https://github.com/yourusername/clock.git
cd clock
./setup.sh
```

Or manually:
```bash
ln -s $(pwd)/clock.py ~/.local/bin/clock
chmod +x clock.py
```

## Usage

```bash
clock              # Show summary
clock day          # Today's activities
clock week         # This week
clock month        # This month
clock summary :week
clock s :month     # Shorthand alias

# New command: start timer with annotation in one step
clock begin work "what you're doing"

# All timewarrior commands work normally
clock stop
clock continue
clock delete @1
```

## Output Format

Instead of:
```
Wk  Date       Day Tags              Start      End        Time     Total
--- ---------- --- --- -------------- ---------- ---------- -------- --------
W47 2025-11-18 Tue project work      09:23:42   13:15:18   03:51:36
                   break             13:45:00   15:30:15   01:45:15
```

You get:
```
Wk     │ Date     │ Tags              │    Start │      End │     Time │    Total
───────┼──────────┼───────────────────┼──────────┼──────────┼──────────┼─────────
W47    │ 11/18    │ project work      │  9:23am  │  1:15pm  │    3h51m │
       │          │ break             │  1:45pm  │  3:30pm  │    1h45m │
```

Changes:
- 24-hour times → 12-hour format (9:23am, 1:15pm)
- HH:MM:SS durations → human-readable (3h51m, 1h45m)
- Aligned columns with proper spacing
- Dates in MM/DD format

## Requirements

- Python 3.6+
- Timewarrior

## Configuration

Clock reads all configuration from Timewarrior:

```bash
timew config
timew config [setting] [value]
```

## Notes

- Fully compatible with all timewarrior features
- Data stored in timewarrior database
- Can mix `clock` and `timew` commands
- Works on Linux, macOS, WSL

## Technical Details

See [DEVELOPMENT.md](DEVELOPMENT.md) for architecture, function documentation, and implementation notes.

## License

MIT
