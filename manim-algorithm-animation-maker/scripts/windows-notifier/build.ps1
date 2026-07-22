param(
    [string]$RuntimeIdentifier = "win-x64"
)

$ErrorActionPreference = "Stop"
$projectDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Join-Path $projectDirectory "ManimRenderNotifier.csproj"
$outputPath = Join-Path $projectDirectory "publish"

dotnet publish $projectPath `
    --configuration Release `
    --runtime $RuntimeIdentifier `
    --self-contained false `
    --output $outputPath

if (-not (Test-Path -LiteralPath (Join-Path $outputPath "ManimRenderNotifier.exe"))) {
    throw "Notifier publish completed without ManimRenderNotifier.exe"
}
