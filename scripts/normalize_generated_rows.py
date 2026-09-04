#!/usr/bin/env python3
"""Extract eight chroma-backed poses and place them in standard transparent cells."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


COLS = 8
CELL_WIDTH = 192
CELL_HEIGHT = 208


def extract_alpha(source: Image.Image) -> Image.Image:
    if source.mode in {"RGBA", "LA"} or "transparency" in source.info:
        rgba = source.convert("RGBA")
        if rgba.getchannel("A").getextrema()[0] == 0:
            return rgba

    rgb = np.asarray(source.convert("RGB"), dtype=np.float32)
    red, green, blue = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    excess = green - np.maximum(red, blue)

    strong_green = (green > red + 80) & (green > blue + 80) & (red < 90) & (blue < 90)
    if not np.any(strong_green):
        raise ValueError("could not identify a green chroma background")

    background_pixels = rgb[strong_green]
    background_rgb = np.median(background_pixels, axis=0)
    background_excess = excess[strong_green]
    transparent_at = float(np.percentile(background_excess, 2))
    opaque_at = 18.0
    if transparent_at <= opaque_at + 20:
        raise ValueError("green background is not sufficiently separated from the subject")

    alpha = np.clip((transparent_at - excess) / (transparent_at - opaque_at), 0.0, 1.0)
    alpha[alpha < 0.08] = 0.0
    alpha[alpha > 0.96] = 1.0

    # Undo green-screen compositing at partially transparent fur edges.
    safe_alpha = np.maximum(alpha[..., None], 0.08)
    foreground = (rgb - (1.0 - alpha[..., None]) * background_rgb) / safe_alpha
    foreground = np.clip(foreground, 0.0, 255.0)
    foreground[alpha == 0] = 0

    rgba = np.dstack((foreground.astype(np.uint8), np.rint(alpha * 255).astype(np.uint8)))
    return Image.fromarray(rgba, mode="RGBA")


def component_groups(mask: np.ndarray) -> list[np.ndarray]:
    """Return eight masks by run-length connected components and weighted 1-D clustering."""
    height, width = mask.shape
    parent: list[int] = []
    runs: list[tuple[int, int, int, int]] = []
    previous: list[tuple[int, int, int]] = []

    def make_label() -> int:
        label = len(parent)
        parent.append(label)
        return label

    def find(label: int) -> int:
        while parent[label] != label:
            parent[label] = parent[parent[label]]
            label = parent[label]
        return label

    def union(first: int, second: int) -> None:
        first_root, second_root = find(first), find(second)
        if first_root != second_root:
            parent[second_root] = first_root

    for y in range(height):
        padded = np.pad(mask[y].astype(np.int8), (1, 1))
        transitions = np.diff(padded)
        starts = np.flatnonzero(transitions == 1)
        ends = np.flatnonzero(transitions == -1)
        current: list[tuple[int, int, int]] = []
        previous_index = 0
        for start, end in zip(starts.tolist(), ends.tolist()):
            label = make_label()
            while previous_index < len(previous) and previous[previous_index][1] < start - 1:
                previous_index += 1
            scan = previous_index
            while scan < len(previous) and previous[scan][0] <= end + 1:
                union(label, previous[scan][2])
                scan += 1
            current.append((start, end, label))
            runs.append((y, start, end, label))
        previous = current

    stats: dict[int, list[float]] = {}
    for y, start, end, label in runs:
        root = find(label)
        length = end - start
        if root not in stats:
            stats[root] = [0.0, 0.0]
        stats[root][0] += length
        stats[root][1] += length * (start + end - 1) / 2

    components = [
        (root, values[0], values[1] / values[0])
        for root, values in stats.items()
        if values[0] >= 16
    ]
    if len(components) < COLS:
        # Adjacent generated poses occasionally touch by a few antialiased pixels.
        # Split at the lowest-occupancy vertical valley near each expected slot
        # boundary so the deterministic normalizer can still isolate eight poses.
        occupancy = mask.sum(axis=0)
        radius = max(2, width // (COLS * 4))
        cuts = [0]
        for index in range(1, COLS):
            target = round(index * width / COLS)
            start = max(cuts[-1] + 1, target - radius)
            end = min(width - 1, target + radius)
            cut = start + int(np.argmin(occupancy[start : end + 1]))
            cuts.append(cut)
        cuts.append(width)
        groups = []
        for left, right in zip(cuts, cuts[1:]):
            group = np.zeros_like(mask, dtype=bool)
            group[:, left:right] = mask[:, left:right]
            if not np.any(group):
                raise ValueError("valley splitting produced an empty pose slot")
            groups.append(group)
        return groups

    centers = np.array([(index + 0.5) * width / COLS for index in range(COLS)], dtype=float)
    for _ in range(40):
        buckets: list[list[tuple[int, float, float]]] = [[] for _ in range(COLS)]
        for component in components:
            index = int(np.argmin(np.abs(centers - component[2])))
            buckets[index].append(component)
        if any(not bucket for bucket in buckets):
            raise ValueError("component clustering left an empty pose slot")
        updated = np.array(
            [sum(area * x for _, area, x in bucket) / sum(area for _, area, _ in bucket) for bucket in buckets]
        )
        if np.allclose(updated, centers, atol=0.1):
            break
        centers = updated

    order = np.argsort(centers)
    root_to_group: dict[int, int] = {}
    for output_index, bucket_index in enumerate(order.tolist()):
        for root, _, _ in buckets[bucket_index]:
            root_to_group[root] = output_index

    groups = [np.zeros_like(mask, dtype=bool) for _ in range(COLS)]
    for y, start, end, label in runs:
        group = root_to_group.get(find(label))
        if group is not None:
            groups[group][y, start:end] = True
    return groups


def normalize_pose(row: Image.Image, mask: np.ndarray, padding: int) -> Image.Image:
    pose = row.copy()
    alpha = np.asarray(pose.getchannel("A")).copy()
    alpha[~mask] = 0
    pose.putalpha(Image.fromarray(alpha, mode="L"))
    bbox = pose.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("empty clustered pose")
    content = pose.crop(bbox)

    max_width = CELL_WIDTH - 2 * padding
    max_height = CELL_HEIGHT - 2 * padding
    scale = min(max_width / content.width, max_height / content.height)
    size = (max(1, round(content.width * scale)), max(1, round(content.height * scale)))
    content = content.resize(size, Image.Resampling.LANCZOS)

    cell = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
    x = (CELL_WIDTH - content.width) // 2
    y = CELL_HEIGHT - padding - content.height
    cell.alpha_composite(content, (x, y))
    return cell


def normalize_row(path: Path, output: Path, padding: int) -> None:
    with Image.open(path) as source:
        row = extract_alpha(source)
    mask = np.asarray(row.getchannel("A")) > 24
    groups = component_groups(mask)

    normalized = Image.new("RGBA", (COLS * CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
    for index, group in enumerate(groups):
        normalized.alpha_composite(normalize_pose(row, group, padding), (index * CELL_WIDTH, 0))
    output.parent.mkdir(parents=True, exist_ok=True)
    normalized.save(output, format="PNG", optimize=True)
    print(f"normalized={output.resolve()}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--padding", type=int, default=8)
    args = parser.parse_args()

    if not 0 <= args.padding < min(CELL_WIDTH, CELL_HEIGHT) // 2:
        parser.error("padding is outside the valid cell range")

    inputs = sorted(args.input_dir.glob("*.png"))
    if not inputs:
        parser.error("input directory contains no PNG rows")
    for path in inputs:
        normalize_row(path, args.output_dir / path.name, args.padding)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
