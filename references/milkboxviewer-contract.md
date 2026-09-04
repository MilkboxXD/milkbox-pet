# MilkboxViewer Resident Image Contract

## Delivery

Deliver two transparent PNG or WebP images. Each image contains 8 columns × 6 rows (48 cells). Every row is one action and always reserves eight frame positions from left to right.

Preferred dimensions for each image are `1536x1248`, producing `192x208` cells. Other dimensions are accepted when the complete 8×6 arrangement is preserved; MilkboxViewer's resident center lets the user adjust the outer crop and internal cut lines before resampling.

Each original upload must be no larger than 12 MiB.

## Sheet 1

| Sheet row | Final atlas row | State | Current use |
| ---: | ---: | --- | --- |
| 1 | 1 | `idle` | General idle and ordinary stopping |
| 2 | 2 | `running-right` | Character movement to the right |
| 3 | 3 | `running-left` | Character movement to the left |
| 4 | 4 | `waving` | User-click interaction |
| 5 | 5 | `reading-writing` | Death Note and streetlamp (planned) |
| 6 | 6 | `rubbing` | Entrance rubbing monument |

## Sheet 2

| Sheet row | Final atlas row | State | Current use |
| ---: | ---: | --- | --- |
| 1 | 7 | `washing` | Back-scrubbing station |
| 2 | 8 | `examining` | Sundial, stone garden, crow lost-and-found kiosk, slow shutter, fir, wind-chime rack, incubator |
| 3 | 9 | `resting` | Long bench, pavilion, foot-soaking stream |
| 4 | 10 | `success` | Reserved game, task, or interaction success |
| 5 | 11 | `failed` | Reserved game, task, or interaction failure |
| 6 | 12 | `grabbed` | Character being picked up and dragged |

## Layout invariants

- Never add, remove, exchange, or rename rows.
- Always retain eight cells per row and left-to-right frame order.
- A row may repeat frames or contain fully transparent unused cells.
- Empty cells keep their original positions and never shift later frames.
- Every non-empty frame remains completely inside its cell.
- The character cannot cross a cell boundary or be clipped by one.
- Keep the character's scale, center, and baseline as consistent as the motion permits.
- Character design, proportions, and main appearance remain consistent across both images.

## Forbidden delivery content

Do not include visible grid lines, borders, row/cell numbers, action labels, instructions, watermarks, UI elements, or scene backgrounds. Transparency must be real alpha, not white, checkerboard, or another simulated background.

## Final pet-v2 atlas

After resident-center processing, the two images combine vertically into one atlas:

- `1536x2496`
- 8 columns × 12 rows
- `192x208` per cell
- Sheet 1 becomes atlas rows 1–6
- Sheet 2 becomes atlas rows 7–12
- PNG or WebP
- Maximum 4 MiB

