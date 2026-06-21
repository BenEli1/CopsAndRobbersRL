param(
    [string]$Output = "assets/evidence/gui-full-match.png",
    [int]$TimeoutSeconds = 20
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public static class NativeWindowCapture {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    public struct Rect { public int Left, Top, Right, Bottom; }

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool SetProcessDPIAware();

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out Rect rect);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool PostMessage(IntPtr hWnd, uint message, IntPtr wParam, IntPtr lParam);

    public static IntPtr FindByTitle(string title) {
        IntPtr found = IntPtr.Zero;
        EnumWindows(delegate(IntPtr hWnd, IntPtr lParam) {
            var text = new StringBuilder(256);
            GetWindowText(hWnd, text, text.Capacity);
            if (text.ToString() == title) {
                found = hWnd;
                return false;
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }
}
"@

[NativeWindowCapture]::SetProcessDPIAware() | Out-Null

$process = Start-Process -FilePath "uv" -ArgumentList @(
    "run", "python", "-m", "cops_and_robbers_rl.main", "gui", "--demo"
) -PassThru
$window = [IntPtr]::Zero

try {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ($window -eq [IntPtr]::Zero -and (Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 250
        $window = [NativeWindowCapture]::FindByTitle("Cops and Robbers RL")
    }
    if ($window -eq [IntPtr]::Zero) {
        throw "GUI window did not appear within $TimeoutSeconds seconds."
    }

    [NativeWindowCapture]::SetForegroundWindow($window) | Out-Null
    Start-Sleep -Milliseconds 500
    $rect = New-Object NativeWindowCapture+Rect
    if (-not [NativeWindowCapture]::GetWindowRect($window, [ref]$rect)) {
        throw "Could not read the GUI window bounds."
    }

    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    $bitmap = New-Object System.Drawing.Bitmap($width, $height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
        $destination = Join-Path $projectRoot $Output
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
        $bitmap.Save($destination, [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Output $destination
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}
finally {
    if ($window -ne [IntPtr]::Zero) {
        [NativeWindowCapture]::PostMessage($window, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
    }
    if (-not $process.HasExited) {
        $process.WaitForExit(3000) | Out-Null
    }
    if (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
    }
}
