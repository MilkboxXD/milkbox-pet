#!/usr/bin/env python3
"""Extract separated poses from reviewed source rows; pack fixed transparent cells."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

from compose_from_rows import parse_hex_color, remove_chroma, save_png
from milkbox_spec import CELL_WIDTH, CELL_HEIGHT, COLS, STATES


def load_source(path: Path, chroma_key=None, tolerance: int = 18) -> Image.Image:
    with Image.open(path) as source:
        if source.format not in {"PNG", "WEBP"}:
            raise ValueError(f"{path}: use the original transparent PNG/WebP, not a JPEG or screenshot")
        rgba = source.convert("RGBA")
    if chroma_key is not None:
        rgba = remove_chroma(rgba, chroma_key, tolerance)
    if rgba.getchannel("A").getextrema()[0] != 0:
        raise ValueError(f"{path}: no fully transparent background; clean the background first")
    return rgba


def frame_count(value) -> int:
    if type(value) is not int or not 1 <= value <= COLS:
        raise ValueError("frame_count must be an approved integer from 1 to 8")
    return value


def check_box(box, size) -> tuple[int, int, int, int]:
    if not isinstance(box, list) or len(box) != 4 or any(type(x) is not int for x in box):
        raise ValueError("box must be [left, top, right, bottom] in integer source pixels")
    left, top, right, bottom = box
    if not (0 <= left < right <= size[0] and 0 <= top < bottom <= size[1]):
        raise ValueError("box lies outside the source image")
    return left, top, right, bottom


def separated_frames(row: Image.Image, count: int, cuts=None) -> list[tuple[Image.Image, int]]:
    """Use only completely transparent gutters; never split through visible pixels.

    Explicit cuts group disconnected props with their owner. No components or faint
    pixels are discarded. Visual review must still check one complete pose per span.
    """
    frame_count(count)
    alpha = np.asarray(row.getchannel("A"))
    if np.any(alpha[0]) or np.any(alpha[-1]) or np.any(alpha[:, 0]) or np.any(alpha[:, -1]):
        raise ValueError("source row touches its crop boundary; expand the box or repair clipped art")
    occupied = np.any(alpha > 0, axis=0)
    if cuts is None:
        edges = np.diff(np.pad(occupied.astype(np.int8), (1, 1)))
        starts = np.flatnonzero(edges == 1)
        ends = np.flatnonzero(edges == -1)
        if len(starts) != count:
            raise ValueError(f"found {len(starts)} separated spans, expected {count}; review cuts or regenerate the row")
        cuts = [int((int(a) + int(b)) // 2) for a, b in zip(ends[:-1], starts[1:])]
    if (not isinstance(cuts, list) or len(cuts) != count - 1
            or any(type(x) is not int for x in cuts)
            or any(not 0 < x < row.width for x in cuts)
            or cuts != sorted(set(cuts))):
        raise ValueError("cuts must contain frame_count - 1 increasing internal x coordinates")
    for x in cuts:
        if occupied[x - 1:x + 1].any():
            raise ValueError(f"cut at x={x} crosses visible pixels; repair the row instead of forced splitting")
    result = []
    for left, right in zip([0] + cuts, cuts + [row.width]):
        frame = row.crop((left, 0, right, row.height))
        if frame.getchannel("A").getbbox() is None:
            raise ValueError("a declared frame is empty")
        result.append((frame, left))
    return result


def pack_frames(frames, padding: int = 8, anchors=None) -> Image.Image:
    """One row-wide scale and registration anchor; no per-pose fit-to-cell zoom."""
    if not 1 <= padding < min(CELL_WIDTH, CELL_HEIGHT) // 2:
        raise ValueError("padding must be at least 1 and less than half a cell")
    if anchors is not None and (not isinstance(anchors, list) or len(anchors) != len(frames)):
        raise ValueError("anchors must contain one [x, y] point per frame, in row coordinates")
    content = []
    for index, (frame, left) in enumerate(frames):
        bbox = frame.getchannel("A").getbbox()
        if anchors is None:
            ax, ay = (bbox[0] + bbox[2]) / 2, bbox[3]
        else:
            point = anchors[index]
            if (not isinstance(point, list) or len(point) != 2
                    or any(type(v) not in (int, float) or not math.isfinite(v) for v in point)):
                raise ValueError("anchor coordinates must be finite numbers")
            ax, ay = point[0] - left, point[1]
        content.append((frame.crop(bbox), bbox[0] - ax, bbox[1] - ay))
    xmin = min(x for image, x, y in content)
    xmax = max(x + image.width for image, x, y in content)
    ymin = min(y for image, x, y in content)
    ymax = max(y + image.height for image, x, y in content)
    # Extra two pixels absorb rounding/resampling at all four safe boundaries.
    inner = padding + 2
    scale = min((CELL_WIDTH - 2 * inner) / (xmax - xmin),
                (CELL_HEIGHT - 2 * inner) / (ymax - ymin), 1.0)
    origin_x = CELL_WIDTH / 2 - scale * (xmin + xmax) / 2
    origin_y = CELL_HEIGHT - inner - scale * ymax
    result = Image.new("RGBA", (COLS * CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
    for index, (image, x, y) in enumerate(content):
        size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
        if image.size != size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        px, py = round(origin_x + scale * x), round(origin_y + scale * y)
        if not (padding <= px and padding <= py
                and px + image.width <= CELL_WIDTH - padding
                and py + image.height <= CELL_HEIGHT - padding):
            raise ValueError("registered frame does not fit its safe cell; review anchors")
        result.alpha_composite(image, (index * CELL_WIDTH + px, py))
    return result


def normalize_row(path: Path, output: Path, padding: int, count: int,
                  cuts=None, anchors=None, chroma_key=None, tolerance: int = 18) -> None:
    row = load_source(path, chroma_key, tolerance)
    result = pack_frames(separated_frames(row, count, cuts), padding, anchors)
    output.parent.mkdir(parents=True, exist_ok=True)
    save_png(result, output)


def normalize_manifest(path: Path, output_dir: Path, padding: int, chroma_key=None,
                       tolerance: int = 18) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("rows") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        raise ValueError("manifest must contain a non-empty rows array")
    sources, coverage, results, counts = {}, {}, {}, {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each row entry must be an object")
        state = entry.get("state")
        if state not in STATES or state in results:
            raise ValueError(f"unknown or duplicate state: {state}")
        try:
            source_path = (path.parent / entry["source"]).resolve()
            if source_path not in sources:
                sources[source_path] = load_source(source_path, chroma_key, tolerance)
                coverage[source_path] = np.zeros((sources[source_path].height, sources[source_path].width), dtype=bool)
            source = sources[source_path]
            box = check_box(entry.get("box", [0, 0, source.width, source.height]), source.size)
            left, top, right, bottom = box
            if coverage[source_path][top:bottom, left:right].any():
                raise ValueError("row boxes overlap")
            coverage[source_path][top:bottom, left:right] = True
            count = frame_count(entry.get("frame_count"))
            row = source.crop(box)
            results[state] = pack_frames(separated_frames(row, count, entry.get("cuts")), padding, entry.get("anchors"))
            counts[state] = count
        except (ValueError, KeyError, TypeError) as exc:
            raise ValueError(f"{state}: {exc}") from exc
    for source_path, source in sources.items():
        if np.any((np.asarray(source.getchannel("A")) > 0) & ~coverage[source_path]):
            raise ValueError(f"{source_path}: visible pixels outside reviewed row boxes; no artwork may be discarded")
    # Validate the entire manifest before writing any output.
    output_dir.mkdir(parents=True, exist_ok=True)
    for state, result in results.items():
        save_png(result, output_dir / f"{state}.png")
    (output_dir / "frame-counts.json").write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    print(f"normalized {len(results)} rows into {output_dir.resolve()}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--manifest", type=Path, help="reviewed source row boxes and approved frame counts")
    inputs.add_argument("--input-dir", type=Path, help="separate raw state.png/state.webp strips")
    parser.add_argument("--frame-counts", type=Path, help="state-to-count JSON; required with --input-dir")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--padding", type=int, default=8)
    parser.add_argument("--chroma-key", type=parse_hex_color)
    parser.add_argument("--chroma-tolerance", type=int, default=18)
    args = parser.parse_args()
    if not 1 <= args.padding < min(CELL_WIDTH, CELL_HEIGHT) // 2:
        parser.error("padding must be at least 1 and less than half a cell")
    if not 0 <= args.chroma_tolerance <= 255:
        parser.error("chroma-tolerance must be between 0 and 255")
    try:
        if args.manifest:
            normalize_manifest(args.manifest, args.output_dir, args.padding, args.chroma_key, args.chroma_tolerance)
        else:
            if not args.frame_counts:
                parser.error("--input-dir requires --frame-counts from the approved motion plan")
            counts = json.loads(args.frame_counts.read_text(encoding="utf-8"))
            if not isinstance(counts, dict) or not counts or any(state not in STATES for state in counts):
                raise ValueError("frame-counts must map known states to approved counts")
            results = {}
            for state, count in counts.items():
                frame_count(count)
                paths = [args.input_dir / f"{state}{suffix}" for suffix in (".png", ".webp")]
                matches = [p for p in paths if p.is_file()]
                if len(matches) != 1:
                    raise ValueError(f"{state}: expected exactly one PNG or WebP source")
                row = load_source(matches[0], args.chroma_key, args.chroma_tolerance)
                try:
                    results[state] = pack_frames(separated_frames(row, count), args.padding)
                except ValueError as exc:
                    raise ValueError(f"{state}: {exc}") from exc
            args.output_dir.mkdir(parents=True, exist_ok=True)
            for state, result in results.items():
                save_png(result, args.output_dir / f"{state}.png")
            (args.output_dir / "frame-counts.json").write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
            print(f"normalized {len(results)} rows into {args.output_dir.resolve()}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
