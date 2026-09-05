#!/usr/bin/env python3
"""Render one eight-frame GIF preview for every MilkboxViewer action row."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from milkbox_spec import COLS, SHEET_1_STATES, SHEET_2_STATES, SHEET_ROWS, SHEET_WIDTH, SHEET_HEIGHT, CELL_WIDTH, CELL_HEIGHT


def extract_rows(path: Path, states: list[str]) -> dict[str, list[Image.Image]]:
    with Image.open(path) as source:
        sheet = source.convert("RGBA")
    if sheet.size != (SHEET_WIDTH, SHEET_HEIGHT):
        raise ValueError("previews require a standardized 1536x1248 sheet")
    result: dict[str, list[Image.Image]] = {}
    for row, state in enumerate(states):
        top = round(row * sheet.height / SHEET_ROWS)
        bottom = round((row + 1) * sheet.height / SHEET_ROWS)
        frames = []
        for col in range(COLS):
            left = round(col * sheet.width / COLS)
            right = round((col + 1) * sheet.width / COLS)
            frames.append(sheet.crop((left, top, right, bottom)))
        while frames and frames[-1].getchannel("A").getbbox() is None:
            frames.pop()
        if not frames or any(frame.getchannel("A").getbbox() is None for frame in frames):
            raise ValueError(f"{state}: blank action or internal empty frame")
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


def render_cut_overlay(path: Path, output: Path) -> None:
    """Review-only overlay; never modify the transparent delivery image."""
    with Image.open(path) as source:
        sheet = source.convert("RGBA")
    if sheet.size != (SHEET_WIDTH, SHEET_HEIGHT):
        raise ValueError("cut overlays require standardized sheets")
    canvas = Image.new("RGBA", sheet.size, (235, 240, 245, 255))
    canvas.alpha_composite(sheet)
    draw = ImageDraw.Draw(canvas)
    for x in range(0, SHEET_WIDTH, CELL_WIDTH):
        draw.line((x, 0, x, SHEET_HEIGHT - 1), fill=(210, 40, 70, 255), width=1)
    for y in range(0, SHEET_HEIGHT, CELL_HEIGHT):
        draw.line((0, y, SHEET_WIDTH - 1, y), fill=(210, 40, 70, 255), width=1)
    draw.rectangle((0, 0, SHEET_WIDTH - 1, SHEET_HEIGHT - 1), outline=(210, 40, 70, 255))
    for row in range(SHEET_ROWS):
        for col in range(COLS):
            x, y = col * CELL_WIDTH, row * CELL_HEIGHT
            draw.rectangle((x + 8, y + 8, x + CELL_WIDTH - 9, y + CELL_HEIGHT - 9),
                           outline=(115, 140, 155, 255))
    canvas.convert("RGB").save(output, format="PNG", optimize=True)


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
    render_cut_overlay(args.sheet1, args.output_dir / "sheet-1-cut-overlay.png")
    render_cut_overlay(args.sheet2, args.output_dir / "sheet-2-cut-overlay.png")
    for state, frames in rows.items():
        output = args.output_dir / f"{state}.gif"
        save_gif(frames, output, args.duration)
        print(f"preview={output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


