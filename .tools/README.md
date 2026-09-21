# Torch Bag 開發工具

本機已找到下列 JDK：

- Java 17：`C:\Program Files\Zulu\zulu-17`
- Java 21：`C:\Program Files\Zulu\zulu-21`

兩套模板各自帶有 Gradle Wrapper，不需要系統安裝 Gradle：

```powershell
pwsh -File .tools/build-forge-1.20.1.ps1
pwsh -File .tools/build-neoforge-1.21.1.ps1
```

需要指定其他 JDK 時：

```powershell
pwsh -File .tools/build-forge-1.20.1.ps1 -JavaHome 'C:\path\to\jdk-17'
pwsh -File .tools/build-neoforge-1.21.1.ps1 -JavaHome 'C:\path\to\jdk-21'
```

只查看 Gradle tasks 時可加 `-Task tasks`。若只想驗證本模組而不下載可選模組的 runtime jar，可用 `-WithCurios:$false` 或 `-WithBackpacks:$false`；compileOnly API 仍會保留。

模板只包含建置與執行設定。兩個版本的 Java 原始碼放在各自的 `src/main/java`，共用資源由 `../common/src/main/resources` 載入。
