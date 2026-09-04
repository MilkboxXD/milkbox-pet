# Milkbox Pet

`milkbox-pet` 是為 MilkboxViewer 居民角色設計的 Codex／ChatGPT Skill。它協助使用者從角色構想或參考圖開始，先完成一張可討論的角色初版，經明確核准後才製作 12 個動畫動作，最後輸出符合 pet-v2 規格的兩張居民圖與 atlas。

本專案參考 OpenAI 官方 [`hatch-pet`](https://github.com/openai/skills/tree/main/skills/.curated/hatch-pet) 的角色一致性、逐列生成、確定性組版與視覺 QA 流程，並改為 MilkboxViewer 的動作與尺寸契約。

## 核心流程

這個 Skill 採用三道明確關卡，不會在資訊不足時自行猜測角色並直接開始動畫製作。

### 1. 確認角色方向

使用者需提供以下任一項：

- 角色型態或物種，例如人物、動物、物件吉祥物、機器人或幻想生物
- 一張角色參考圖

建議同時說明畫風、主要配色、服裝、標記或固定配件。若資料不足，Skill 會先詢問，不會呼叫圖像生成，也不會從專案名稱自行推測角色。

### 2. 生成初版並討論

收到足夠方向後，只生成一張透明背景的全身角色概念圖。使用者可以針對外型、比例、臉部、配色、服裝、標記、配件與畫風持續修改。

這個階段不會產生動畫列、spritesheet 或 atlas。

### 3. 核准後選擇動畫模式

只有在使用者同時確認目前造型，並明確要求開始動畫製作後，才會進入 12 動作流程。例如：

```text
確認這個造型，開始做動畫。
```

```text
這版可以，請產生 12 個動作。
```

```text
用這張定稿製作 MilkboxViewer 圖集。
```

單純回覆「很可愛」「看起來不錯」或提出初版修改，不代表已授權製作動畫。

明確核准動畫後，Skill 會讓使用者選擇：

| 模式 | 初始生成方式 | 適合情境 |
| --- | --- | --- |
| 混合模式（建議） | 先生成兩張圖，每張包含六段橫向連續動畫；失敗動作再個別重做 | 兼顧生成額度與局部修補品質 |
| 快速模式 | 同樣生成兩張圖，以整張為修復單位 | 優先減少生成次數 |
| 精修模式 | 分別生成 12 段橫向連續動畫 | 優先控制每個動作與最小修復範圍 |

若使用者請 Skill 自行決定，預設採混合模式。等待模式選擇期間不會開始生成動畫。

## 使用方式

在 Codex 中使用：

```text
$milkbox-pet 幫我設計一位居民角色
```

在支援 Skills 的 ChatGPT 中使用：

```text
@milkbox-pet 幫我設計一位居民角色
```

也可以一開始就提供比較完整的方向：

```text
$milkbox-pet
我想做一隻圓滾滾的橘色狐狸居民，貼紙插畫風，戴深綠色小圍巾。
先生成一張全身初版給我討論，在我明確確認前不要製作動畫。
```

若已經有核准過的角色圖，可以直接附圖並說明：

```text
這張是已定稿的居民角色。請用它製作 MilkboxViewer 的 12 個動作圖集。
```

也可以直接指定動畫模式：

```text
確認這個造型。請使用混合模式：先生成兩張圖，每張包含六段由左到右的連續逐格動畫；只有失敗的動作才個別修補。
```

## 安裝

安裝時需保留完整資料夾，不能只複製 `SKILL.md`，因為動畫規格、QA 規則與組版工具位於 `references/` 和 `scripts/`。

Codex 個人 Skill 的建議位置：

```text
~/.codex/skills/milkbox-pet/
```

Windows 範例：

```powershell
Copy-Item -Recurse -Force `
  "C:\path\to\milkbox-pet" `
  "$env:USERPROFILE\.codex\skills\milkbox-pet"
```

重新開啟對話後即可使用 `$milkbox-pet`。若要在 ChatGPT 網頁版使用，應安裝或分享完整 Skill／Plugin；把 `SKILL.md` 單獨當作 Knowledge 上傳，只能提供文字規則，無法保證組版與驗證腳本會執行。

## 動作排列

每張交付圖固定為 8 欄 × 6 列，每列保留 8 個影格位置。

第一張圖：

| 列 | 動作 | 用途 |
| ---: | --- | --- |
| 1 | `idle` | 一般待機 |
| 2 | `running-right` | 向右移動 |
| 3 | `running-left` | 向左移動 |
| 4 | `waving` | 點擊互動 |
| 5 | `reading-writing` | 閱讀或書寫互動 |
| 6 | `rubbing` | 拓印互動 |

第二張圖：

| 列 | 動作 | 用途 |
| ---: | --- | --- |
| 1 | `washing` | 刷洗互動 |
| 2 | `examining` | 觀察與檢查 |
| 3 | `resting` | 坐下或休息 |
| 4 | `success` | 成功反應 |
| 5 | `failed` | 失敗反應 |
| 6 | `grabbed` | 被抓起拖曳 |

完整動作語意請參考 [`references/animation-rows.md`](references/animation-rows.md)。

## 輸出規格

原始交付：

- 2 張 PNG 或 WebP
- 每張 8 欄 × 6 列
- 建議尺寸 `1536 × 1248 px`
- 每格 `192 × 208 px`
- 真正 Alpha 透明背景
- 單張不超過 12 MiB

最終 pet-v2 atlas：

- `1536 × 2496 px`
- 8 欄 × 12 列
- 每格 `192 × 208 px`
- PNG 或 WebP
- 不超過 4 MiB

若生成工具無法輸出精確尺寸，可先保留完整 8×6 排列，再交由 MilkboxViewer 居民中心調整切割線。完整契約請參考 [`references/milkboxviewer-contract.md`](references/milkboxviewer-contract.md)。

## 混合模式（預設）

先以核准的角色初版作為共同參考，生成兩張圖片。每張包含六段上下排列的橫向動畫；每段是一個動作，由左到右連續演進，最多 8 個影格。不足 8 格時，後方未使用位置保持真正的透明空白。一般圖片工具一次只會回傳一張圖片，因此通常是兩個生成工作，而不是一個工作同時回傳兩張。

`8×6` 是切割與交付格式，不是建議直接交給生圖模型的提示詞。提示模型時不要只寫「8×6 網格」或「八格橫列」，應描述「連續逐格動畫、由左到右、最多 8 個影格、未使用位置透明」。例如：

```text
Create six stacked horizontal animation sequences for the approved character. Each sequence depicts one continuous action progressing from left to right in up to eight successive frames. Keep character identity, scale, center, and baseline consistent. If an action needs fewer than eight frames, leave the unused trailing frame positions fully transparent. No text, labels, borders, visible grid lines, UI, or scene background.
```

將兩張均分網格標準化並合併成 atlas：

```powershell
python scripts/standardize_sheets.py `
  --sheet1 generated/sheet-1.png `
  --sheet2 generated/sheet-2.png `
  --output-dir delivery
```

接著執行格式驗證與 GIF 預覽。若某個動作出現錯誤姿勢、角色漂移、跨格或方向錯誤，只重新生成該動作的橫向連續動畫；最多 8 個影格，不足的位置留透明空白。

例如修補第一張圖的 `waving`：

```powershell
python scripts/replace_sheet_row.py `
  --sheet delivery/milkbox-pet-sheet-1.png `
  --sheet-number 1 `
  --state waving `
  --replacement repairs/waving.png `
  --output repaired/milkbox-pet-sheet-1.png
```

例如修補第二張圖的 `failed`：

```powershell
python scripts/replace_sheet_row.py `
  --sheet delivery/milkbox-pet-sheet-2.png `
  --sheet-number 2 `
  --state failed `
  --replacement repairs/failed.png `
  --output repaired/milkbox-pet-sheet-2.png
```

`--state` 會決定動作應屬於哪一張圖及哪一列；如果 `--sheet-number` 不相符，工具會停止，避免把修補列放錯位置。

完成所有修補後，再用 `standardize_sheets.py` 處理修好的兩張圖，以重建 atlas，然後重新驗證並產生預覽。

## 快速模式

快速模式與混合模式同樣先生成兩張圖片，每張包含六段橫向連續動畫，再使用 `standardize_sheets.py`、驗證器與 GIF 預覽。差別是快速模式不會自動逐列修補；若驗證失敗，使用者可以選擇重新生成整張，或切換成混合模式修補特定動作。

## 精修模式：從 12 段連續動畫組版

分別生成 12 段透明 PNG 或 WebP 橫向連續動畫。每段從左到右演進，最多 8 個影格；若動作只需要較少影格，未使用的後方位置保持透明。將檔案放入以下資料夾：

```text
rows/
  idle.png
  running-right.png
  running-left.png
  waving.png
  reading-writing.png
  rubbing.png
  washing.png
  examining.png
  resting.png
  success.png
  failed.png
  grabbed.png
```

組版工具會把每段動畫視為八個等寬的保留位置；這是組版規則，不是生圖提示詞。執行：

```powershell
python scripts/compose_from_rows.py `
  --rows-dir rows `
  --output-dir delivery
```

輸出：

```text
delivery/
  milkbox-pet-sheet-1.png
  milkbox-pet-sheet-2.png
  milkbox-pet-v2-atlas.png
```

若來源使用單色去背背景：

```powershell
python scripts/compose_from_rows.py `
  --rows-dir rows `
  --output-dir delivery `
  --chroma-key 00FF00 `
  --chroma-tolerance 18
```

去背後仍需人工檢查邊緣與角色顏色是否被誤刪。

## 驗證圖片

```powershell
python scripts/validate_pet_images.py `
  --sheet1 delivery/milkbox-pet-sheet-1.png `
  --sheet2 delivery/milkbox-pet-sheet-2.png `
  --atlas delivery/milkbox-pet-v2-atlas.png `
  --json-out delivery/validation.json
```

驗證器會檢查：

- PNG／WebP 格式
- Alpha 透明度
- 標準尺寸
- 上傳圖與 atlas 檔案大小限制
- 完全空白列
- 角色像素是否碰到均分格線邊緣
- 透明像素是否保留隱藏 RGB 殘值

非標準尺寸的兩張原始圖只會產生警告，因為居民中心仍能調整切割線；非標準尺寸的最終 atlas 則會驗證失敗。

## 產生動畫預覽

```powershell
python scripts/render_previews.py `
  --sheet1 delivery/milkbox-pet-sheet-1.png `
  --sheet2 delivery/milkbox-pet-sheet-2.png `
  --output-dir previews
```

這會輸出 12 個 GIF。請依 [`references/qa-rubric.md`](references/qa-rubric.md) 檢查角色一致性、動作語意、循環跳動、朝向、裁切、跨格與透明背景。

## 開發與測試

需求：

- Python 3.10 或更新版本
- [Pillow](https://pypi.org/project/pillow/)

執行端到端 smoke test：

```powershell
python tests/smoke_test.py
```

測試會在暫存資料夾驗證三條確定性路徑：12 個動作列組版、兩張完整圖的標準化與合併，以及單一失敗列替換。測試也會完成格式驗證與 12 個 GIF 預覽，結束後自動移除測試圖片。

驗證 Skill 結構：

```powershell
python <skill-creator-path>/scripts/quick_validate.py .
```

## 專案結構

```text
milkbox-pet/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── animation-rows.md
│   ├── milkboxviewer-contract.md
│   └── qa-rubric.md
├── scripts/
│   ├── compose_from_rows.py
│   ├── milkbox_spec.py
│   ├── replace_sheet_row.py
│   ├── render_previews.py
│   ├── standardize_sheets.py
│   └── validate_pet_images.py
└── tests/
    └── smoke_test.py
```

`output/` 是實際生成或測試角色時的工作資料，不是 Skill 本身的必要組成。
