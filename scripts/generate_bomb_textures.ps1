[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root 'artwork\ender_eye_reference.png'
$output = Join-Path $root 'common\src\main\resources\assets\torch_bag\textures\item'
New-Item -ItemType Directory -Force -Path $output | Out-Null
$eye = [System.Drawing.Bitmap]::FromFile($source)

try {
    foreach ($tier in 1..3) {
        $image = New-Object System.Drawing.Bitmap 16, 16, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        for ($y = 0; $y -lt 16; $y++) {
            for ($x = 0; $x -lt 16; $x++) {
                $pixel = $eye.GetPixel($x, $y)
                if ($pixel.A -eq 0) { continue }
                $light = [Math]::Max(0, [Math]::Min(255, [int](0.30 * $pixel.R + 0.59 * $pixel.G + 0.11 * $pixel.B)))
                $distance = [Math]::Sqrt(($x - 7.5) * ($x - 7.5) + ($y - 7.5) * ($y - 7.5))
                if ($distance -gt 4.2) {
                    # Coal-dark outer shell, with a small tint for each level.
                    $v = [Math]::Max(24, [int]($light * 0.48))
                    if ($tier -eq 1) { $r = $v; $g = [Math]::Min(255, $v + 12); $b = $v }
                    elseif ($tier -eq 2) { $r = [Math]::Min(255, $v + 22); $g = [Math]::Min(255, $v + 9); $b = $v }
                    else { $r = [Math]::Min(255, $v + 14); $g = $v; $b = [Math]::Min(255, $v + 32) }
                }
                elseif ($light -lt 35) { $r = 20; $g = 24; $b = 20 }
                elseif ($tier -eq 1) {
                    $r = [Math]::Min(255, [int]($light * 0.65)); $g = [Math]::Min(255, [int]($light * 1.30)); $b = [Math]::Min(255, [int]($light * 0.55))
                }
                elseif ($tier -eq 2) {
                    $r = [Math]::Min(255, [int]($light * 1.38)); $g = [Math]::Min(255, [int]($light * 0.88)); $b = [Math]::Min(255, [int]($light * 0.25))
                }
                else {
                    $r = [Math]::Min(255, [int]($light * 0.90)); $g = [Math]::Min(255, [int]($light * 1.25)); $b = [Math]::Min(255, [int]($light * 1.45))
                }
                $image.SetPixel($x, $y, [System.Drawing.Color]::FromArgb($pixel.A, $r, $g, $b))
            }
        }
        $sparks = if ($tier -eq 1) { @(@(7,1),@(8,1)) } elseif ($tier -eq 2) { @(@(3,3),@(12,2),@(13,4)) } else { @(@(7,0),@(1,7),@(14,7),@(12,2)) }
        foreach ($point in $sparks) {
            $spark = if ($tier -eq 3) { [System.Drawing.Color]::FromArgb(255,210,255,255) } else { [System.Drawing.Color]::FromArgb(255,255,190,45) }
            $image.SetPixel($point[0], $point[1], $spark)
        }
        $roman = @('', 'i', 'ii', 'iii')[$tier]
        $path = Join-Path $output "torch_bomb_$roman.png"
        $image.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
        $image.Dispose()
        Write-Output $path
    }
}
finally { $eye.Dispose() }
