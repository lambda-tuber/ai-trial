Add-Type -AssemblyName System.Windows.Forms

# 引数で幅を受け取る（指定がなければデフォルト 800）
$maxWidth = if ($args.Count -ge 1) { [int]$args[0] } else { 800 }

# 元スクリーンサイズ
$screenWidth = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width

# マウス位置取得
$mouse = [System.Windows.Forms.Cursor]::Position
$mouseX = $mouse.X
$mouseY = $mouse.Y

# 縮小比率計算
$ratio = $maxWidth / $screenWidth
$scaledMouseX = [int]($mouseX * $ratio)
$scaledMouseY = [int]($mouseY * $ratio)

# JSON出力（type=text 形式）
$text = "x=$scaledMouseX, y=$scaledMouseY"
$json = "{`"type`":`"text`",`"text`":`"$text`"}"
Write-Output $json
