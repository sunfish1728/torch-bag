# 火把袋開發環境

這個資料夾包含兩套互相獨立的開發專案。主程式 Java 放在各版本自己的 `src/main/java`；共用貼圖、繁體中文、簡體中文、英文與 Curios 欄位資料放在 `common/src/main/resources`。配方與物品標籤因版本格式不同，分別放在兩版資源目錄。

| 模板 | Minecraft | Loader | JDK | Loader 版本 |
| --- | --- | --- | --- | --- |
| `forge-1.20.1` | 1.20.1 | Forge | 17 | 47.4.10 |
| `neoforge-1.21.1` | 1.21.1 | NeoForge | 21 | 21.1.251 |

模組 ID 是 `torch_bag`，Java group/package 根是 `dev.torchbag`。兩套模板都保留 `client`、`server`、`gameTestServer`、`data` run 設定；GameTest namespace 已指向 `torch_bag`。

## 建置

系統目前沒有 Gradle，兩套模板已附 Gradle Wrapper。Windows PowerShell 可直接執行：

```powershell
pwsh -File .tools/build-forge-1.20.1.ps1
pwsh -File .tools/build-neoforge-1.21.1.ps1
```

腳本預設使用本機已找到的 `C:\Program Files\Zulu\zulu-17` 與 `C:\Program Files\Zulu\zulu-21`，不會修改系統環境變數；若 Java 裝在別處，使用 `-JavaHome` 指定。

## 可選整合依賴

Curios 使用作者 Maven `https://maven.theillusivec4.top/`：

- Forge API/runtime：`top.theillusivec4.curios:curios-forge:5.13.0+1.20.1`
- NeoForge API/runtime：`top.theillusivec4.curios:curios-neoforge:9.5.1+1.21.1`

Sophisticated Backpacks 與 Sophisticated Core 使用官方 CurseForge Maven `https://www.cursemaven.com`，依賴以 CurseForge project/file ID 固定：

- Forge：Backpacks `3.26.1.2132`（project `422301`, file `8828182`），Core `1.5.1.2335`（project `618298`, file `8839328`）
- NeoForge：Backpacks `3.26.3.2158`（project `422301`, file `8845926`），Core `1.5.1.2341`（project `618298`, file `8838842`）

依賴是 `compileOnly` 加開發執行用的 `runtimeOnly`/`localRuntime`，所以火把袋沒有安裝這些模組時仍可編譯主程式；實際整合測試 run 會自動載入它們。

## 測試與開發啟動

腳本的 `-Task` 可以設成 `runClient`、`runServer` 或 `runGameTestServer`。例如：

```powershell
pwsh -File .tools/build-forge-1.20.1.ps1 -Task runGameTestServer
pwsh -File .tools/build-neoforge-1.21.1.ps1 -Task runGameTestServer
```

也可進入版本資料夾，指定適合的 `JAVA_HOME`，直接呼叫 wrapper。以 NeoForge 為例：

```powershell
$env:JAVA_HOME='C:\Program Files\Zulu\zulu-21'
.\gradlew.bat runGameTestServer -PwithCurios=false -PwithBackpacks=false
.\gradlew.bat runClient -PvisualTest=true
```

`withCurios` 和 `withBackpacks` 預設為 `true`，只影響開發執行時載入的模組；編譯介面依賴仍保留。`visualTest` 預設為 `false`，開啟後會在真正的 Minecraft 渲染器中截取一張火把袋畫面，再自動結束遊戲。圖片位於該版 `run/screenshots/`。

`build` 負責編譯和打包；遊戲內測試需另外執行 `runGameTestServer`。測試類別 `BagGameTests`、`ClientVisualTest` 和空白測試結構不會打包進成品。

Forge 開發環境已配置 Mixin refmap 轉換，以便 Curios 及精妙背包的發佈版本能在官方名稱對照的開發環境中執行。

## 修改共同行為

Java 共同行為及兩版差異維護於 `scripts/generate_sources.py`，JSON 維護於 `scripts/generate_resources.py`，爆彈貼圖由 `scripts/generate_bomb_textures.ps1` 產生，畫面測試維護於 `scripts/generate_visual_test.py`。使用 Python 3／PowerShell 執行腳本即可重新產生已納入原始碼的檔案。一般編譯不需要執行這些腳本。

測試結果與已確認範圍見 `TESTING.md`。
