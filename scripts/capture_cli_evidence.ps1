param([string]$OutputDirectory = "assets/evidence")

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
Add-Type -AssemblyName System.Drawing

function Save-ConsoleCapture {
    param([string]$Title, [string]$Command, [string[]]$Lines, [string]$FileName)

    $font = New-Object System.Drawing.Font("Consolas", 15)
    $smallFont = New-Object System.Drawing.Font("Segoe UI", 11)
    $lineHeight = 24
    $width = 1200
    $height = 92 + (($Lines.Count + 1) * $lineHeight) + 28
    $bitmap = New-Object System.Drawing.Bitmap($width, $height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.Clear([System.Drawing.Color]::FromArgb(15, 23, 42))
        $graphics.FillRectangle([System.Drawing.Brushes]::DarkSlateBlue, 0, 0, $width, 58)
        $graphics.DrawString($Title, $font, [System.Drawing.Brushes]::White, 22, 16)
        $graphics.DrawString(
            "Captured from a real local command on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')",
            $smallFont,
            [System.Drawing.Brushes]::LightGray,
            22,
            64
        )
        $y = 92
        $graphics.DrawString("> $Command", $font, [System.Drawing.Brushes]::LightGreen, 22, $y)
        $y += $lineHeight
        foreach ($line in $Lines) {
            $graphics.DrawString($line, $font, [System.Drawing.Brushes]::Gainsboro, 22, $y)
            $y += $lineHeight
        }
        $destination = Join-Path (Join-Path $projectRoot $OutputDirectory) $FileName
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
        $bitmap.Save($destination, [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Output $destination
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
        $font.Dispose()
        $smallFont.Dispose()
    }
}

$matchCommand = "uv run cops-and-robbers play --seed 42 --output results/report_email_preview.json"
$matchOutput = & uv run cops-and-robbers play --seed 42 --output results/report_email_preview.json 2>&1
if ($LASTEXITCODE -ne 0) { throw "Headless match failed." }
Save-ConsoleCapture "Deterministic six-game match" $matchCommand $matchOutput "headless-match.png"

$mcpCommand = "uv run python -m cops_and_robbers_rl.main mcp-smoke"
$mcpOutput = & uv run python -m cops_and_robbers_rl.main mcp-smoke 2>&1
if ($LASTEXITCODE -ne 0) { throw "MCP smoke failed." }
Save-ConsoleCapture "Local cop/thief MCP contract smoke" $mcpCommand $mcpOutput "mcp-smoke.png"
