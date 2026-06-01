# Changelog

## 2026-06-01

- Refactored UI codebase: Extracted Notes section into a dedicated `NotesFrame` class in `ui_components.py` for better modularity.
- Fixed UI layout inconsistencies: Removed double-layer frame from the `CompactSolverFrame` and `NotesFrame`.
- Restored compact layout for the Notes section: Embedded the save icon and hint text directly into the frame's title bar (using `labelwidget`).
- Added row-number click copy for the result sheet, using the same copy behavior as the built-in tksheet copy action.
- Added a compact Notes save icon beside the Notes title without adding extra layout height.
- Added Notes export support for TXT and CSV formats.
- Fixed Notes CSV export header spacing so `Deviation%` and `E24` are saved as separate columns.
- Adjusted Notes save defaults so TXT/CSV extensions are applied according to the selected file type.
