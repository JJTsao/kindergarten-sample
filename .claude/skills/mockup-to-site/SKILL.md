---
name: mockup-to-site
description: 將設計稿圖片（mockup PNG/JPG）復刻為一頁式靜態網站，並（可選）以使用者提供的真實照片/插畫素材升級為 production 成品。當使用者要求「依設計稿建站」、「復刻 SampleX.png」、「mockup 轉網站」時使用。流程分兩階段：Phase 1 自動建站到「佔位完成」；Phase 2 真實素材交接（生圖 brief、自動裁切素材、最佳化、drop-in 替換）。
---

# Mockup → Site：設計稿復刻一頁式網站

把單張設計稿忠實復刻為純靜態一頁式網站（HTML + CSS + 少量 vanilla JS，無 build step），並能在使用者提供真實素材後升級為 production 成品。

## 原則

- **文案逐字抄錄**，不自行編寫或「優化」設計稿上的文字。
- **兩階段**：Phase 1 不需外部素材就能做到「視覺完整的佔位版」；Phase 2 把佔位素材換成真實照片/插畫（需使用者提供，因本環境無法生圖、圖庫 CDN 也被擋）。
- **接縫先留好**：Phase 1 的佔位素材用**語意命名＋固定長寬比**，Phase 2 才能 drop-in 替換、完全不動 HTML/CSS。
- **驗證迴圈跑到吻合為止**：截圖 → 與設計稿並排比對 → 修正 → 再截圖。
- **復刻 ≠ 完工**：設計稿是「縮小的窄桌面版」，忠實復刻後在真實寬螢幕（1440–2560）會顯空。要補一個獨立的「桌機密度 pass」（見專節）——關鍵認知：那是**尺寸問題（字級/圖片/版心照窄稿定死），不是用裝飾填補**。

## 環境備忘（實測）

- Playwright chromium 已裝：截圖前綴 `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`。Node 全域模組在 `/opt/node22/lib/node_modules`（需 `NODE_PATH` 指過去才能 `require('playwright')`）。
- 沒有 scipy → 連通元件用 numpy + BFS 自己寫。
- **圖庫 CDN（Unsplash/Pexels/Picsum）回 403**、無法生圖；Google Fonts 可連線（字體用 Noto Sans TC 近似）。
- **使用者貼上的「預覽圖」不會落地成檔案**，PIL 讀不到；要可處理的檔案必須走「附加檔案」（訊息會出現 `@/root/.claude/uploads/...` 路徑）或 git push 進 repo。一則訊息附檔上限約 5 張。

---

# Phase 1 — 自動建站到「佔位完成」

### 1. 看圖：尺寸與結構
```python
from PIL import Image
img = Image.open('SampleX.png'); print(img.size)  # 常是縮小的桌面版，用 ~1200px container 復刻；但版心別寫死，production 要轉 fluid（見「桌機密度」）
```
先 Read 整張掌握區塊順序（nav / hero / features / … / footer）。

### 2. 判讀內容：切片放大逐區閱讀
原尺寸小字不可讀。垂直切 5–6 片各放大 2 倍逐片 Read；細部（卡片內文、footer）再針對性裁小區放大 3 倍。產出**內容清單**：每區標題/內文/按鈕/連結/卡片欄位，逐字記錄。
```python
w,h=img.size; n=6
for i in range(n):
    t,b=h*i//n,h*(i+1)//n
    img.crop((0,t,w,b)).resize((w*2,(b-t)*2),Image.LANCZOS).save(f'/tmp/s{i}.png')
```

### 3. 取色：建立設計 tokens
```python
img.convert('RGB').quantize(colors=16).convert('RGB')   # 主色盤
# 強調色（量少不進主色盤）：依色相過濾像素取樣
```
整理成 `:root` CSS custom properties（品牌色、底色、強調色、文字色）。

### 4. 佔位素材（從設計稿裁切）
寫 `scripts/extract_assets.py`：**內縮 2–4px** 避開設計稿照片自帶圓角/卡片底色（圓角交給 CSS）、避開重疊裝飾；小圖 Lanczos 2x＋輕銳化；**語意命名＋固定長寬比**（`class-junior.jpg`、`teacher-emily.jpg`…）這是 Phase 2 的接縫。逐張 Read 檢查、微調座標。
Icon/裝飾**不裁圖**（裁出來糊且帶背景）：簡單幾何用開源 icon set 的 SVG path；品牌 logo 先 SVG 重繪（若有原檔，Phase 2 再忠實化）。

### 5. 建站
- `index.html` 語意化區塊（`section` 帶 id 供錨點）。
- `css/styles.css`：tokens → 共用元件（按鈕/卡片/section tag）→ 各區 → RWD（桌面 4 欄 → 平板 2 欄 → 手機 1 欄；斷點 ~1024 / 640）。
- `js/main.js` 僅手機漢堡選單。動效保守（hover 浮起/變色），不發明設計稿沒有的。

### 6. 驗證迴圈
```bash
python3 -m http.server 8077 &
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers npx playwright screenshot --full-page --viewport-size=1280,800 http://localhost:8077 /tmp/site.png
```
截圖縮至與設計稿同寬，切 6 段並排比對，逐段 Read。檢查序：區塊順序 → 配色 → 字級層次 → 間距 → 裝飾。
- **間距**：設計稿等比放大後常比實作更密；量各區高度比（`getBoundingClientRect`）找出「被拉鬆」處，收緊 section padding（協調收 ~1.4–1.6x 的鬆度，但別壓到卡片擠）。
- **裝飾**：設計稿在 hero/CTA 以外常很乾淨；若要更豐富，加**適度**spot 點綴（雲/星/葉/柔和 blob），墊在 `.deco-layer`（`position:absolute;inset:0;overflow:hidden;z-index:0`）下層、`.container{z-index:1}`，放留白角落、不擋內容；手機別整批隱藏。**點綴是呼應設計稿氛圍，不是拿來補寬螢幕的「太空」——那是尺寸問題（見「桌機密度」），別靠裝飾填。**
另截 390px 手機版確認不破版。

---

# 桌機密度 pass：寬螢幕的留白控制（復刻後必做）

設計稿多是縮小的窄桌面版，忠實復刻後在真實寬螢幕會顯空——**不是內容不夠，是字級／圖片／版心都照窄稿尺寸定死，在寬畫面上相對縮小、留白主導**。補一個獨立 pass，照以下**概念**走（不要直接套數字，每個專案量過再定範圍）：

- **留白是被擠出來的剩餘量，別直接設定它。** 約束內容（版心 `max-width`、欄寬、字級），留白自然收斂；寫死的 px 留白跨寬度必飄。
- **用範圍（`clamp`）取代固定值。** 版心、字級、圖高都給「地板＋天花板＋隨寬度流動」。固定值是為單一寬度調的，換寬度就破——典型坑：欄寬固定但字級隨寬度變 → 某些中間寬度欄內空一截。
- **字與主圖隨寬度一起放大**，讓寬螢幕像「放大版」而非「小島浮在空白裡」。但要封頂：行長過長難讀、圖片過度裁切、貼邊滿版顯廉價——別推到極端。
- **欄寬貼著內容**（`max-content`／內容驅動），別分配固定 `fr` 比例而在欄內留空。
- **圖片高度設天花板**（`height: clamp(...)` + `object-fit: cover`）：版寬驅動的圖高會隨寬度抽長，造出隨視窗浮動的垂直留白帶；封頂即收掉。
- **多欄列的欄距是 grid 軌道決定的，放大字填不滿。** 要收斂散開的多欄（如 footer），改版型（重配軌道）；並避免單一高欄（如 5 項直排）撐高整列 → flatten 成橫排。
- **桌機限定、平板手機不動**：改動寫進 `@media (min-width:1025px)`（與既有 ≤1024 斷點互補，不會外漏），收尾回截 390 確認。
- **量化驗證、別憑感覺**：`getBoundingClientRect` 在 1920/1440/1280/1025 量側溝、頂部空白帶、欄距，measure → 調 → 截圖。瀏覽器會快取 CSS，量測前先換 `link.href` 加時間戳強制刷新。

---

# Phase 2 — 真實素材交接（升級為 production）

佔位圖源自設計稿（低解析），要換成真實照片/插畫才完整。本環境不能生圖 → 由使用者提供；skill 的價值在**把交接講清楚、讓替換機械化**。

### A. 照片 brief（給使用者生圖）
逐張列：**檔名（＝佔位檔名）、用途、生成尺寸、可直接貼 ChatGPT 的英文 prompt**。輸出成 `photo-brief.md` 給使用者。
- **尺寸**：生圖工具支援 1024×1024 / 1536×1024 / 1024×1536；橫幅用 1536×1024、人像/頭像用 1024×1024。最終裁切交給 CSS `object-fit:cover`，來源夠大即可。
- **⚠️ 變化矩陣（避免整組「長一樣」）**：同類照片若每張都同前綴、同「孩子圍桌室內」，會視覺疲勞。**保留統一的光線/色調（＝協調），但刻意拉開**：景別（遠/中/特寫）、角度（平視/俯拍/側面）、場景（桌邊/地墊/戶外/繪本角/實驗/律動）、服裝色、人數。每個 prompt 加 `different children, classroom, clothing from other photos`。
- **生圖訣竅**：每張**開新對話**生（同對話會沿用上一張的房間/小孩/衣服）；AI 人像易「太端正、置中如證件照」→ 指定 `candid three-quarter angle, looking slightly off-camera, shallow depth of field`，但臉仍要夠大且近中心，圓形裁切才不歪。

### B. 裝飾/插畫素材（sprite sheet → 自動裁切）
使用者常給一張**去背透明 PNG 素材表**。用 alpha 連通元件自動裁成獨立透明小圖：
```python
# numpy + BFS（無 scipy）：對 alpha>32 的 mask 做 8-連通標記，取每個元件 bbox
# 多部件的圖示（太陽含光芒、彩虹含雲）以「手動分組 bbox 的聯集」裁；裁後 .getbbox() 去透明邊
```
存成語意命名透明 PNG（`assets/deco/rainbow.png`…），用 `<img class="deco">` 編排進各區 `.deco-layer`（角落/留白、低透明、`pointer-events:none`）。**素材表裡若有對應 icon（對話泡/燈泡/愛心/盾牌）可直接升級特色卡 icon、笑臉太陽可換標題裝飾**——比手刻 SVG 質感好。

### C. 見證頭像用「插畫 avatar」而非真人照
家長見證用真人 AI 頭像易顯僵硬/假臉。改用**簡約扁平 SVG avatar**（圓底＋不同髮型/膚色/配色），刻意扁平風→不會有廉價感，也避開假臉。師資則維持真實照片（增信任），但用 candid 鏡位。

### D. 素材交付 logistics
- 收檔方式：**git push 進 `assets/img/`（最穩、保留解析度、零歧義）** 或「附加檔案」（有 `@/root/...` 路徑才落地）。貼預覽圖無效。
- 收到後：**drop-in 替換同名檔，HTML/CSS 不動**。若使用者推到 master 而打磨在分支 → 把 master 併進分支匯合（通常無衝突）。

### E. Web 最佳化（重要）
生圖原檔常 ~2MB/張。依**顯示尺寸**縮放＋壓縮：
```python
# 橫幅 max 900–1600px、人像 ~520px；JPEG quality 82–85, optimize=True, progressive=True
```
實測 31MB → ~1.3MB，顯示尺寸下無可見損失。

### F. 收尾
重截桌機/手機驗證真實素材裁切（尤其圓形頭像置中、hero 出血）；可產一份 base64 內嵌的**自包含單檔** HTML 給使用者離線預覽（`file://` 直開、手機可看）。

---

## 交付/分支
- 開發在指定 feature 分支，commit 訊息清楚；完成 push 後（經同意才）開 PR。
- Skill 放 repo `.claude/skills/`，之後同類設計稿（Sample2–4）直接觸發套用。
