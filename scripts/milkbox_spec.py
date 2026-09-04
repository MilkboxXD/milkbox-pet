"""Shared MilkboxViewer pet-v2 geometry and row contract."""

COLS = 8
SHEET_ROWS = 6
ATLAS_ROWS = 12
CELL_WIDTH = 192
CELL_HEIGHT = 208
SHEET_WIDTH = COLS * CELL_WIDTH
SHEET_HEIGHT = SHEET_ROWS * CELL_HEIGHT
ATLAS_WIDTH = SHEET_WIDTH
ATLAS_HEIGHT = ATLAS_ROWS * CELL_HEIGHT
MAX_UPLOAD_BYTES = 12 * 1024 * 1024
MAX_ATLAS_BYTES = 4 * 1024 * 1024

STATES = [
    "idle",
    "running-right",
    "running-left",
    "waving",
    "reading-writing",
    "rubbing",
    "washing",
    "examining",
    "resting",
    "success",
    "failed",
    "grabbed",
]

SHEET_1_STATES = STATES[:SHEET_ROWS]
SHEET_2_STATES = STATES[SHEET_ROWS:]

