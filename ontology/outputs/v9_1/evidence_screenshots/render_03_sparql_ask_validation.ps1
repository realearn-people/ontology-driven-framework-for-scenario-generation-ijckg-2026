
Add-Type -AssemblyName System.Drawing
$text = Get-Content -Path "ontology/outputs/v9_1/evidence_screenshots/03_sparql_ask_validation.txt" -Raw
$font = New-Object System.Drawing.Font "Consolas", 18, ([System.Drawing.FontStyle]::Regular)
$titleFont = New-Object System.Drawing.Font "Consolas", 18, ([System.Drawing.FontStyle]::Bold)
$lines = $text -split "`r?`n"
$lineHeight = 30
$padding = 34
$width = 1800
$height = [Math]::Max(420, ($lines.Count * $lineHeight) + ($padding * 2))
$bmp = New-Object System.Drawing.Bitmap $width, $height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$bg = [System.Drawing.ColorTranslator]::FromHtml("#101820")
$green = [System.Drawing.ColorTranslator]::FromHtml("#7EE787")
$white = [System.Drawing.ColorTranslator]::FromHtml("#D6E2F0")
$gray = [System.Drawing.ColorTranslator]::FromHtml("#8FA3B8")
$yellow = [System.Drawing.ColorTranslator]::FromHtml("#FFD166")
$g.Clear($bg)
$y = $padding
foreach ($line in $lines) {
    if ($line.StartsWith("PS ")) {
        $brush = New-Object System.Drawing.SolidBrush $green
        $g.DrawString($line, $titleFont, $brush, 28, $y)
        $brush.Dispose()
    } elseif ($line.StartsWith("#")) {
        $brush = New-Object System.Drawing.SolidBrush $yellow
        $g.DrawString($line, $titleFont, $brush, 28, $y)
        $brush.Dispose()
    } elseif ($line.Trim().Length -eq 0) {
        # keep blank line spacing
    } elseif ($line.Contains("PASS") -or $line.Contains("True") -or $line.Contains("0 detected")) {
        $brush = New-Object System.Drawing.SolidBrush $green
        $g.DrawString($line, $font, $brush, 28, $y)
        $brush.Dispose()
    } else {
        $brush = New-Object System.Drawing.SolidBrush $white
        $g.DrawString($line, $font, $brush, 28, $y)
        $brush.Dispose()
    }
    $y += $lineHeight
}
$bmp.Save("ontology/outputs/v9_1/evidence_screenshots/03_sparql_ask_validation.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
$font.Dispose()
$titleFont.Dispose()
Write-Output "ontology/outputs/v9_1/evidence_screenshots/03_sparql_ask_validation.png"
