# ⏰ Clock

> A painfully elegant CLI wrapper for [Timewarrior](https://timewarrior.net/). Because tracking time shouldn't feel like a punishment.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](#)
[![Python](https://img.shields.io/badge/python-3.6+-green.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](#)

## What Problem Does This Solve?

You love Timewarrior. But then you run a command and see:

```
24-hour times. HH:MM:SS durations. Misaligned columns.
No thank you.
```

**Clock** fixes that.

## Features

✨ **12-hour time format** — `9:45am` not `09:45`
📊 **Human durations** — `1h32m` not `1:32:00`
📐 **Aligned columns** — With fancy box-drawing characters
🎯 **Smart aliases** — `clock s :month` works
🚀 **New `begin` command** — Start + annotate in one shot
🔄 **Full pass-through** — All timewarrior commands work

## Quick Start

```bash
git clone https://github.com/yourusername/clock.git
cd clock
./setup.sh
```

Then:
```bash
clock        # Shows summary (better than help)
clock day    # Today's time
clock week   # This week's time
clock month  # This month's time
```

## Usage

### Commands

```bash
# View time reports (in beautiful 12-hour format)
clock day
clock week
clock month
clock summary :week
clock summary :month

# Check version
clock version

# All timewarrior commands work too
clock stop
clock continue
clock delete @1
```

### The Magic: `clock begin`

Start a timer and add a note in one command:

```bash
clock begin work "fixing that weird bug"
```

Instead of:
```bash
timew start work
timew ann "fixing that weird bug"
```

### Shorthand Aliases

```bash
clock s :month    # Same as: clock summary :month
```

## Before & After

### Stock Timewarrior
```
Wk  Date       Day Tags              Start      End        Time     Total
--- ---------- --- --- -------------- ---------- ---------- -------- --------
W47 2025-11-18 Tue project work      09:23:42   13:15:18   03:51:36
                   break             13:45:00   15:30:15   01:45:15
```

### Clock
```
Wk     │ Date     │ Tags              │    Start │      End │     Time │    Total
───────┼──────────┼───────────────────┼──────────┼──────────┼──────────┼─────────
W47    │ 11/18    │ project work      │  9:23am  │  1:15pm  │    3h51m │
       │          │ break             │  1:45pm  │  3:30pm  │    1h45m │
```

Yeah. That's the difference. ✨

## Real Example

```bash
$ clock summary :yesterday

Wk     │ Date     │ Tags              │    Start │      End │     Time │    Total
───────┼──────────┼───────────────────┼──────────┼──────────┼──────────┼─────────
W48    │ 11/25    │ meeting urgent    │  8:00am  │  9:30am  │    1h30m │
       │          │ coding            │ 10:00am  │  1:15pm  │    3h15m │
       │          │ lunch             │  1:15pm  │  2:00pm  │    45m   │
       │          │ code review       │  2:00pm  │  5:45pm  │    3h45m │
```

Readable. Clean. Professional. You'll actually want to look at it.

## Installation

### Option 1: Automated (Recommended)
```bash
git clone https://github.com/yourusername/clock.git
cd clock
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual
```bash
ln -s $(pwd)/clock.py ~/.local/bin/clock
chmod +x clock.py
```

Then verify:
```bash
clock help
```

## Requirements

- **Python** 3.6+
- **Timewarrior** (with `timew` CLI available)

## How It Works

Clock wraps timewarrior and transforms the output:

1. **Time conversion** — 24h → 12h format
2. **Duration formatting** — HH:MM:SS → Xh Ym
3. **Column alignment** — Right-align times, box-drawing borders
4. **Date formatting** — YYYY-MM-DD → MM/DD
5. **Smart display** — All your data, but readable

See [DEVELOPMENT.md](DEVELOPMENT.md) for technical details.

## Configuration

Clock reads all settings from Timewarrior. Configure normally:

```bash
timew config
timew config [setting] [value]
```

## Notes

✅ Fully compatible with all timewarrior features
✅ Data stored in same timewarrior database
✅ Mix `clock` and `timew` commands freely
✅ Works on Linux, macOS, WSL

## Troubleshooting

**`clock: command not found`**
- Ensure `~/.local/bin` is in your `$PATH`: `echo $PATH`
- Or run directly: `python3 /path/to/clock.py day`

**Times look weird**
- Make sure timewarrior is configured: `timew show`
- Clock just wraps timewarrior—if timew is broken, clock is broken

## Contributing

Found a bug? Have an idea? [Open an issue](https://github.com/yourusername/clock/issues) or submit a PR.

## License

MIT. Go wild.

---

<div align="center">

**Made by someone who loves time tracking but hated squinting at 24-hour time.**

</div>
