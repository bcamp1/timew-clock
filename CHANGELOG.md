# Changelog

All notable changes to Clock are documented in this file.

## [1.1.0] - 2025-11-26

### Added
- **Grand Total label** - Summary output now displays "Grand Total: Xh Ym" instead of unlabeled duration at the bottom
- Grand Total is automatically right-aligned to the table edge, adapting to different table widths

### Changed
- **Header styling** - Removed vertical dividers from header row for cleaner appearance while keeping dividers in separator and data rows
- **Column alignment** - Fixed header column titles to align properly with separator and data rows

### Fixed
- Header vertical dividers no longer misaligned with separator row dividers
- Header column titles now align correctly with their respective data columns

## [1.0.0] - 2025-11-26

### Initial Release

#### Features
- 12-hour time format display (9:45am instead of 09:45)
- Human-readable duration format (1h32m instead of 1:32:00)
- Professional table styling with box-drawing characters (│, ─, ┼)
- Improved column alignment and readability
- Date formatting (MM/DD instead of YYYY-MM-DD)
- Command shorthand aliases (`clock s` → `clock summary`)
- New `begin` command (start timer + add annotation in one step)
- Version command (`clock version`)
- Full pass-through support for all timewarrior commands
- Default behavior shows summary instead of help

#### Commands Implemented
- `clock` - Show summary
- `clock day|week|month` - View formatted reports
- `clock summary [options]` - Detailed summary with 12h times and human durations
- `clock begin <tags> "<annotation>"` - Start timer with annotation
- `clock version` - Display version number
- `clock help [topic]` - Show help with "clock" references
- All timewarrior commands via pass-through

#### Processing Pipeline
1. Time conversion (24h → 12h)
2. Duration formatting (HH:MM:SS → Xh Ym)
3. Column alignment with box-drawing borders
4. Date formatting (YYYY-MM-DD → MM/DD)
5. Column removal and consolidation
6. Professional table styling

---

**Format Note**: This changelog follows [Keep a Changelog](https://keepachangelog.com/) conventions.
