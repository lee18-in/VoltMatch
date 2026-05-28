# 🤖 VoltMatch AI 協作最高指導原則 (System Prompt)

身為協助開發此專案的 AI 助手，請嚴格遵守以下「憲法等級」的規範：

## 1. 程式碼完整性 (Code Integrity)

- **絕對禁止**刪除或修改任何檔案的「表頭註解 (Header Comments)」。

## 2. 核心算法限制 (Core Algorithm Constraints)

- **窮舉所有可能性 (Exhaustive Search)** 是本專案的核心初衷（為了算盡所有組合，而非單純找單一最佳解）。
- **絕對禁止**使用會破壞或跳過窮舉邏輯的演算法優化（例如：二分搜尋法、啟發式演算法等）。請接受大範圍下運算時間較長的事實，這是系統設計特性。

## 3. 審查與重構流程 (Design Review Process)

- 若使用者要求「幫忙設計審查 (Design Review)」或優化效能，請**先列出可優化的項目清單**。
- 待討論並確認後，再提供對應的程式碼，切勿未經同意直接給出一大段重構後的程式碼。

## 4. 專案打包規範 (Packaging Guidelines)

- 專案內附有開源授權聲明 `CREDITS.txt`。當提供任何打包指令或腳本（如 PyInstaller）時，務必確保將此檔案一併打包放入執行檔所在目錄。
