# Script để deploy CropWise API lên Render

Write-Host "=== CROPWISE API DEPLOYMENT ===" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra model.pth
if (-not (Test-Path "model.pth")) {
    Write-Host "❌ Error: model.pth không tồn tại!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ model.pth đã sẵn sàng" -ForegroundColor Green

# Setup Git
Write-Host ""
Write-Host "📦 Đang setup Git repository..." -ForegroundColor Yellow

git branch -M main

# Lấy GitHub username
Write-Host ""
$username = Read-Host "Nhập GitHub username của bạn (hiện tại: nubibo123)"
if ([string]::IsNullOrWhiteSpace($username)) {
    $username = "nubibo123"
}

# Add remote (nếu chưa có)
$remoteExists = git remote | Select-String -Pattern "origin"
if (-not $remoteExists) {
    git remote add origin "https://github.com/$username/cropwise-api.git"
    Write-Host "✅ Đã thêm remote origin" -ForegroundColor Green
} else {
    Write-Host "ℹ️ Remote origin đã tồn tại" -ForegroundColor Blue
}

# Push to GitHub
Write-Host ""
Write-Host "🚀 Đang push code lên GitHub..." -ForegroundColor Yellow
Write-Host "⚠️ Bạn sẽ cần nhập GitHub credentials nếu được yêu cầu" -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ ĐÃ PUSH CODE THÀNH CÔNG!" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== BƯỚC TIẾP THEO ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1️⃣ Truy cập: https://render.com" -ForegroundColor White
    Write-Host "2️⃣ Đăng nhập bằng GitHub" -ForegroundColor White
    Write-Host "3️⃣ Click 'New +' → 'Web Service'" -ForegroundColor White
    Write-Host "4️⃣ Chọn repository: cropwise-api" -ForegroundColor White
    Write-Host "5️⃣ Settings:" -ForegroundColor White
    Write-Host "   - Name: cropwise-api" -ForegroundColor Gray
    Write-Host "   - Runtime: Docker" -ForegroundColor Gray
    Write-Host "   - Instance Type: Free" -ForegroundColor Gray
    Write-Host "6️⃣ Click 'Create Web Service'" -ForegroundColor White
    Write-Host "7️⃣ Đợi 5-10 phút để deploy" -ForegroundColor White
    Write-Host "8️⃣ Copy URL từ Render (dạng: https://cropwise-api-xxxx.onrender.com)" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️ LƯU Ý:" -ForegroundColor Yellow
    Write-Host "- Free tier có 512MB RAM (có thể không đủ cho PyTorch)" -ForegroundColor Yellow
    Write-Host "- Nếu gặp lỗi OOM, cân nhắc nâng cấp lên Starter plan ($7/tháng)" -ForegroundColor Yellow
    Write-Host "- Hoặc dùng Hugging Face Spaces (16GB RAM, miễn phí)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📱 Sau khi có URL từ Render, cập nhật file diseaseService.ts:" -ForegroundColor Cyan
    Write-Host "const API_URL = 'https://your-render-url.onrender.com';" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR WHEN PUSHING!" -ForegroundColor Red
    Write-Host ""
    Write-Host "You may need to:" -ForegroundColor Yellow
    Write-Host "1. Create 'cropwise-api' repository on GitHub first" -ForegroundColor Yellow
    Write-Host "2. Setup GitHub credentials or Personal Access Token" -ForegroundColor Yellow
    Write-Host "3. Run: git push -u origin main --force" -ForegroundColor Yellow
    Write-Host ""
}
