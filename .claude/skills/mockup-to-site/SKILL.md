---
name: mockup-to-site
description: 將設計稿圖片（mockup PNG/JPG）復刻為一頁式靜態網站。當使用者要求「依設計稿建站」、「復刻 SampleX.png」、「mockup 轉網站」時使用。流程涵蓋判讀文案、取色、裁切照片素材、建構 HTML/CSS、截圖比對驗證。
---

# Mockup → Site：設計稿復刻一頁式網站

把單張設計稿圖片忠實復刻為純靜態一頁式網站（HTML + CSS + 少量 vanilla JS，無 build step）。

## 原則

- **文案逐字抄錄**，不自行編寫或「優化」設計稿上的文字。
- **照片從設計稿裁切**（本環境網路政策封鎖圖庫 CDN，無法外抓）；icon 與裝飾用 inline SVG 重繪。
- **驗證迴圈跑到吻合為止**：截圖 → 與設計稿並排比對 → 修正 → 再截圖。

## 流程

### 1. 看圖：尺寸與整體結構

```python
from PIL import Image
img = Image.open('SampleX.png')
print(img.size)  # 注意：設計稿通常是縮小的桌面版（如 941px 寬），實作以 1200px container 放大重建
```

先 Read 整張圖掌握區塊順序（nav / hero / features / ... / footer）。

### 2. 判讀內容：切片放大逐區閱讀

設計稿原尺寸下小字不可讀。垂直切成 5–6 片、各放大 2 倍逐片 Read；
細部文字（卡片內文、footer）再針對性裁小區域放大 3 倍。

```python
w, h = img.size
n = 6
for i in range(n):
    top, bot = h*i//n, h*(i+1)//n
    img.crop((0, top, w, bot)).resize((w*2, (bot-top)*2), Image.LANCZOS).save(f'/tmp/slice{i}.png')
```

產出**內容清單**：每個區塊的標題、內文、按鈕、連結、卡片欄位，逐字記錄。

### 3. 取色：建立設計 tokens

```python
# 主色盤
small = img.convert('RGB').quantize(colors=16).convert('RGB')
# 強調色（量少不會進主色盤）：依色相條件過濾像素
reds = Counter(c for c in data if c[0]>180 and c[1]<110 and c[2]<110)
```

整理成 CSS custom properties（品牌色、底色、強調色、文字色）。

### 4. 裁切照片素材

寫 `scripts/extract_assets.py`（PIL），規則：

- **內縮裁切** 2–4px 避開設計稿照片自帶的圓角與卡片底色；圓角由 CSS 重新套用。
- **避開重疊裝飾**（愛心、blob、陰影壓在照片邊上的區域）。
- 小圖用 **Lanczos 2x 放大＋輕度銳化**（`ImageEnhance.Sharpness ~1.3`）再輸出，優於瀏覽器放大。
- 輸出 JPEG quality ≥ 90；**語意命名**（`class-junior.jpg`、`teacher-emily.jpg`），日後可 drop-in 換真實照片。
- 每張裁切結果逐一 Read 肉眼檢查，微調座標。

Icon／裝飾**不裁圖**（裁出來 ~40px 模糊帶背景）：

- 簡單幾何 icon → 開源 icon set（Lucide/Heroicons）的 SVG path，inline 進 HTML 可換色。
- 品牌 logo、複雜插畫（校舍、熱氣球）→ 先扁平風 SVG 重繪，驗證時與原圖並排比對，明顯遜色才 fallback 裁切原圖（限純色底、只縮小不放大）。
- 大面積 blob、波浪分隔 → SVG path / CSS。

### 5. 建站

- `index.html`：語意化區塊（`header/nav`、`section` 帶 id 供錨點、`footer`）。
- `css/styles.css`：`:root` tokens → 共用元件（按鈕、卡片、section tag）→ 各區塊 → RWD（桌面 4 欄 → 平板 2 欄 → 手機 1 欄；斷點約 960px / 640px）。
- `js/main.js`：僅手機漢堡選單 toggle。
- 字體：Google Fonts Noto Sans TC（本環境可連線）。
- 動效保守：只加 hover 回饋（卡片浮起、按鈕變色），不發明設計稿沒有的大動效。

### 6. 驗證迴圈

```bash
python3 -m http.server 8000 &
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers npx playwright screenshot \
  --full-page --viewport-size=1280,800 http://localhost:8000 /tmp/site.png
```

```python
# 截圖縮至與設計稿同寬，切 6 段並排合成比對圖，逐段 Read 檢查
```

檢查順序：區塊順序 → 配色 → 字級層次 → 間距 → 細節裝飾。修正後重截，直到吻合。
另截 `--viewport-size=390,844` 手機版確認不破版。最後把比對圖傳給使用者。
