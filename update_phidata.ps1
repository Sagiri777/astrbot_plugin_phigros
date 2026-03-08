# Phigros 数据源更新脚本

$baseUrl = "https://phidata.tx4.de5.net"
$targetDir = "resources/data"
$infoFiles = @(
    "info/avatar.txt",
    "info/chapters.txt",
    "info/chapters.json",
    "info/illustration.txt",
    "info/single.txt",
    "info/difficulty.tsv",
    "info/info.tsv",
    "info/tips.txt",
    "info/collection.tsv"
)

# 创建目标目录
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force
}

# 下载文件
foreach ($file in $infoFiles) {
    $url = "$baseUrl/$file"
    $fileName = Split-Path $file -Leaf
    $targetPath = "$targetDir\$fileName"
    
    Write-Host "正在下载: $file"
    try {
        Invoke-WebRequest -Uri $url -OutFile $targetPath -UseBasicParsing
        Write-Host "✓ 下载完成: $fileName"
    } catch {
        Write-Host "✗ 下载失败: $fileName - $($_.Exception.Message)"
    }
}

Write-Host "\n数据源更新完成！"
