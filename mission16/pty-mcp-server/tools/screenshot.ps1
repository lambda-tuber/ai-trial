Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 引数で最大幅を受け取る（指定なければデフォルト 800）
$maxWidth = if ($args.Count -ge 1) { [int]$args[0] } else { 800 }

# 元スクリーンサイズ
$screenWidth = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width
$screenHeight = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height

# デスクトップキャプチャ
$bmp = New-Object System.Drawing.Bitmap($screenWidth, $screenHeight)
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen(0,0,0,0,$bmp.Size)

# 縮小比率計算
$ratio = $maxWidth / $screenWidth
$newWidth = [int]($screenWidth * $ratio)
$newHeight = [int]($screenHeight * $ratio)

# 縮小
$smallBmp = New-Object System.Drawing.Bitmap($bmp, $newWidth, $newHeight)

# 日時付きファイル名作成
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$fileName = "screenshot_$timestamp.png"
$filePath = Join-Path -Path $PWD -ChildPath $fileName

# PNGとして保存
$smallBmp.Save($filePath,[System.Drawing.Imaging.ImageFormat]::Png)

# メモリにPNG保存（Base64用）
$ms = New-Object System.IO.MemoryStream
$smallBmp.Save($ms,[System.Drawing.Imaging.ImageFormat]::Png)
$b64 = [Convert]::ToBase64String($ms.ToArray())

# JSON出力
$json = "{`"type`":`"image`",`"mime_type`":`"image/png`",`"data`":`"$b64`"}"
Write-Output $json

# 保存完了メッセージを stderr に出力
[Console]::Error.WriteLine("Saved screenshot to $filePath")

