# Animation Rows

Prompt each state as one continuous animation progressing from left to right in at most eight successive frames. Do not describe it to the image model merely as an “8-slot row” or “grid.” If the motion needs fewer than eight frames, leave the unused trailing positions fully transparent; repeat a frame only for an intentional timing hold. The delivery layout still reserves all eight positions, so later content must never shift into the unused area.

| Atlas row | State | Motion direction |
| ---: | --- | --- |
| 1 | `idle` | Calm breathing, blinking, or small weight shift; visibly alive but low-distraction |
| 2 | `running-right` | Clear right-facing travel with alternating gait and stable scale |
| 3 | `running-left` | Clear left-facing travel; redraw or safely mirror per frame |
| 4 | `waving` | Limb rises, waves, and returns; avoid floating wave marks |
| 5 | `reading-writing` | Read, turn/look, write or mark, then settle; keep any book or tool attached to the pose |
| 6 | `rubbing` | Press paper/tool to a vertical surface and rub repeatedly; no full scene or monument background |
| 7 | `washing` | Reaching and scrubbing/washing motion suitable for a back-scrubbing interaction |
| 8 | `examining` | Lean, look, inspect, compare, or study; avoid adding UI, text, or unrelated props |
| 9 | `resting` | Sit, recline, breathe, or relax in a loop; do not bake a bench or pavilion scene into the sprite unless it is part of the resident identity |
| 10 | `success` | Readable happy or triumphant reaction; avoid detached confetti, icons, and text |
| 11 | `failed` | Readable disappointed or deflated reaction; any tears or smoke must touch the character and remain inside the cell |
| 12 | `grabbed` | Suspended, gently dangling, compressed, or reacting while being dragged; no drawn cursor, hand, UI, or scene |

Rows should loop without a large first-to-last pop. Directional cadence must not become static or reverse accidentally. Empty cells are permitted by the file contract, but a production action should normally contain enough distinct poses to communicate its purpose.
