#!/usr/bin/env python3
"""Render one eight-frame GIF preview for every MilkboxViewer action row."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from milkbox_spec import COLS, SHEET_1_STATES, SHEET_2_STATES, SHEET_ROWS


def extract_rows(path: Path, states: list[str]) -> dict[str, list[Image.Image]]:
    with Image.open(path) as source:
        sheet = source.convert("RGBA")
    result: dict[str, list[Image.Image]] = {}
    for row, state in enumerate(states):
        top = round(row * sheet.height / SHEET_ROWS)
        bottom = round((row + 1) * sheet.height / SHEET_ROWS)
        frames = []
        for col in range(COLS):
            left = round(col * sheet.width / COLS)
            right = round((col + 1) * sheet.width / COLS)
            frames.append(sheet.crop((left, top, right, bottom)))
        result[state] = frames
    return result


def save_gif(frames: list[Image.Image], path: Path, duration: int) -> None:
    max_width = max(frame.width for frame in frames)
    max_height = max(frame.height for frame in frames)
    normalized = []
    for frame in frames:
        canvas = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))
        canvas.alpha_composite(frame, ((max_width - frame.width) // 2, (max_height - frame.height) // 2))
        normalized.append(canvas)
    normalized[0].save(
        path,
        save_all=True,
        append_images=normalized[1:],
        duration=[duration] * len(normalized),
        loop=0,
        disposal=2,
        transparency=0,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet1", type=Path, required=True)
    parser.add_argument("--sheet2", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--duration", type=int, default=140, help="milliseconds per frame")
    args = parser.parse_args()

    if args.duration <= 0:
        parser.error("--duration must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = extract_rows(args.sheet1, SHEET_1_STATES)
    rows.update(extract_rows(args.sheet2, SHEET_2_STATES))
    for state, frames in rows.items():
        output = args.output_dir / f"{state}.gif"
        save_gif(frames, output, args.duration)
        print(f"preview={output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

