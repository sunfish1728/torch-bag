[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$JavaHome = 'C:\Program Files\Zulu\zulu-21',
    [string]$Task = 'build',
    [bool]$WithCurios = $true,
    [bool]$WithBackpacks = $true
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path (Join-Path $JavaHome 'bin\java.exe'))) {
    throw "找不到 Java 21: $JavaHome。請用 -JavaHome 指定 JDK 21 資料夾。"
}
$env:JAVA_HOME = $JavaHome
$env:Path = "$(Join-Path $JavaHome 'bin');$env:Path"
$exitCode = 1
Push-Location (Join-Path $PSScriptRoot '..\neoforge-1.21.1')
try {
    & .\gradlew.bat $Task --no-daemon "-PwithCurios=$($WithCurios.ToString().ToLower())" "-PwithBackpacks=$($WithBackpacks.ToString().ToLower())"
    $exitCode = $LASTEXITCODE
}
finally { Pop-Location }
exit $exitCode
