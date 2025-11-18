# HƯỚNG DẪN DEPLOY LÊN HUGGING FACE SPACES

## Bước 1: Tạo tài khoản Hugging Face

1. Truy cập: https://huggingface.co/join
2. Đăng ký tài khoản miễn phí
3. Xác nhận email

## Bước 2: Tạo Space mới

1. Truy cập: https://huggingface.co/new-space
2. Điền thông tin:
   - **Space name**: `cropwise-api` (hoặc tên khác)
   - **License**: MIT
   - **Select the Space SDK**: **Gradio**
   - **Space hardware**: **CPU basic** (miễn phí, 16GB RAM)
   - **Visibility**: Public
3. Click **Create Space**

## Bước 3: Upload files lên Space

### Cách 1: Upload qua Web UI (Đơn giản nhất)

1. Sau khi tạo Space, click tab **Files**
2. Click **Add file** → **Upload files**
3. Upload các file sau (kéo thả hoặc chọn):
   - `app_gradio.py` (đổi tên thành `app.py` khi upload)
   - `model.pth`
   - `yolo_leaf_model.pt`
   - `requirements_hf.txt` (đổi tên thành `requirements.txt` khi upload)
   - `README.md`
4. Click **Commit changes to main**

### Cách 2: Upload qua Git (Nâng cao)

```powershell
# Clone space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/cropwise-api
cd cropwise-api

# Copy files
Copy-Item ..\cropwise-api\app_gradio.py .\app.py
Copy-Item ..\cropwise-api\model.pth .
Copy-Item ..\cropwise-api\yolo_leaf_model.pt .
Copy-Item ..\cropwise-api\requirements_hf.txt .\requirements.txt
Copy-Item ..\cropwise-api\README.md .

# Commit và push (có thể mất 5-10 phút vì file lớn)
git lfs track "*.pth"
git lfs track "*.pt"
git add .
git commit -m "Initial commit"
git push
```

## Bước 4: Đợi Build

1. Space sẽ tự động build (5-10 phút)
2. Theo dõi logs ở tab **Logs**
3. Khi thấy "Running on public URL", là thành công!

## Bước 5: Lấy API URL

Space URL sẽ có dạng:
```
https://YOUR_USERNAME-cropwise-api.hf.space
```

API endpoint cho mobile:
```
https://YOUR_USERNAME-cropwise-api.hf.space/predict
```

## Bước 6: Cập nhật React Native App

Mở file `services/diseaseService.ts` và thay đổi:

```typescript
const API_URL = 'https://YOUR_USERNAME-cropwise-api.hf.space';
```

## Bước 7: Test

### Test Web UI:
Truy cập: `https://YOUR_USERNAME-cropwise-api.hf.space`

### Test API:
```powershell
curl -X POST "https://YOUR_USERNAME-cropwise-api.hf.space/predict" `
  -F "file=@test_image.jpg"
```

## ✅ Ưu điểm của Hugging Face Spaces

- ✅ **Miễn phí 16GB RAM** (đủ cho PyTorch + YOLO + DenseNet)
- ✅ **Không sleep** như Render free tier
- ✅ **Git LFS support** cho model lớn
- ✅ **Web UI miễn phí** với Gradio
- ✅ **HTTPS sẵn có**
- ✅ **Community support tốt**

## ⚠️ Lưu ý

1. **File size limit**: 10GB cho free tier (đủ cho models)
2. **Build time**: 5-10 phút do phải tải PyTorch
3. **Cold start**: Lần đầu gọi API có thể chậm (3-5s)
4. **Quota**: Unlimited requests (fair use)

## 🔧 Troubleshooting

### Nếu build fail:
- Kiểm tra `requirements.txt` có đúng format
- Đảm bảo `app.py` không có lỗi syntax
- Xem logs để debug

### Nếu API timeout:
- Tăng timeout trong React Native app lên 60s
- Hoặc nâng cấp lên GPU hardware (miễn phí 2h/ngày)

### Nếu không detect được lá:
- Kiểm tra ảnh input có rõ ràng
- Thử giảm `conf=0.25` xuống `conf=0.1` trong code
