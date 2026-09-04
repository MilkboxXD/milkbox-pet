#!/usr/bin/env python3
"""Replace one MilkboxViewer action row in a delivery sheet."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from compose_from_rows import load_normalized_row, parse_hex_color, save_png
from milkbox_spec import (
    CELL_HEIGHT,
    CELL_WIDTH,
    SHEET_ROWS,
    SHEET_WIDTH,
    STATES,
)
from standardize_sheets import normalize_sheet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--sheet-number", type=int, choices=(1, 2), required=True)
    parser.add_argument("--state", choices=STATES, required=True)
    parser.add_argument("--replacement", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chroma-key", type=parse_hex_color)
    parser.add_argument("--chroma-tolerance", type=int, default=18)
    parser.add_argument("--padding", type=int, default=8)
    args = parser.parse_args()

    if not args.sheet.is_file():
        parser.error(f"sheet does not exist: {args.sheet}")
    if not args.replacement.is_file():
        parser.error(f"replacement row does not exist: {args.replacement}")
    if not 0 <= args.chroma_tolerance <= 255:
        parser.error("--chroma-tolerance must be between 0 and 255")
    if not 0 <= args.padding < min(CELL_WIDTH, CELL_HEIGHT) // 2:
        parser.error("--padding is outside the valid cell range")

    atlas_row = STATES.index(args.state)
    sheet_number = 1 if atlas_row < SHEET_ROWS else 2
    sheet_row = atlas_row % SHEET_ROWS
    if args.sheet_number != sheet_number:
        parser.error(f"{args.state} belongs to sheet {sheet_number}, not sheet {args.sheet_number}")

    base = normalize_sheet(args.sheet, None, args.chroma_tolerance)
    frames = load_normalized_row(
        args.replacement,
        args.chroma_key,
        args.chroma_tolerance,
        args.padding,
    )

    transparent_row = Image.new("RGBA", (SHEET_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
    base.paste(transparent_row, (0, sheet_row * CELL_HEIGHT))
    for column, frame in enumerate(frames):
        base.alpha_composite(frame, (column * CELL_WIDTH, sheet_row * CELL_HEIGHT))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    save_png(base, args.output)
    print(f"state={args.state}")
    print(f"expected_sheet={sheet_number}")
    print(f"sheet_row={sheet_row + 1}")
    print(f"output={args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
