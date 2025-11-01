# HƯỚNG DẪN DEPLOY CROPWISE API LÊN RENDER

## Bước 1: Tạo GitHub Repository

1. Truy cập: https://github.com/new
2. Repository name: `cropwise-api`
3. Description: `CropWise Disease Detection API`
4. Chọn **Public**
5. **KHÔNG** chọn "Add a README file"
6. Click **Create repository**

## Bước 2: Push Code lên GitHub

Mở PowerShell trong thư mục `cropwise-api` và chạy:

```powershell
git branch -M main
git remote add origin https://github.com/nubibo123/cropwise-api.git
git push -u origin main
```

Nếu bị lỗi "remote origin already exists", chạy:
```powershell
git remote remove origin
git remote add origin https://github.com/nubibo123/cropwise-api.git
git push -u origin main
```

Bạn sẽ cần nhập GitHub credentials hoặc Personal Access Token.

## Bước 3: Deploy lên Render

1. Truy cập: https://render.com
2. Click **Get Started** hoặc **Sign Up**
3. Chọn **Sign up with GitHub**
4. Authorize Render truy cập GitHub
5. Sau khi đăng nhập, click **New +** (góc trên bên phải)
6. Chọn **Web Service**
7. Click **Connect account** nếu được yêu cầu
8. Tìm và chọn repository: **cropwise-api**
9. Click **Connect**

### Cấu hình Web Service:

- **Name**: `cropwise-api` (hoặc tên bạn muốn)
- **Region**: Singapore (gần Việt Nam nhất)
- **Branch**: `main`
- **Runtime**: **Docker** (Render sẽ tự detect Dockerfile)
- **Instance Type**: **Free**
- Các trường khác để mặc định

10. Click **Create Web Service**
11. Đợi 5-10 phút để Render build và deploy

## Bước 4: Lấy API URL

1. Sau khi deploy thành công, bạn sẽ thấy URL ở trên cùng
2. Format: `https://cropwise-api-xxxx.onrender.com`
3. Copy URL này

## Bước 5: Test API

Truy cập: `https://your-render-url.onrender.com/`

Bạn sẽ thấy:
```json
{
  "message": "CropWise Disease Detection API",
  "version": "1.0"
}
```

## Bước 6: Cập nhật React Native App

Mở file `services/diseaseService.ts` và thay đổi:

```typescript
// Thay đổi từ:
const API_URL = 'http://192.168.0.106:8001';

// Sang:
const API_URL = 'https://cropwise-api-xxxx.onrender.com'; // Thay bằng URL của bạn
```

**LƯU Ý**: 
- Không cần port `:8001` cho Render URL
- Phải dùng `https://` chứ không phải `http://`

## Bước 7: Test App

1. Save file `diseaseService.ts`
2. Reload app trên điện thoại (shake device → Reload)
3. Chụp ảnh hoặc chọn từ gallery
4. App sẽ gọi API từ Render thay vì localhost

## ⚠️ LƯU Ý QUAN TRỌNG

### Free Tier Limitations:
- **RAM**: 512MB (có thể không đủ cho PyTorch + ResNet18)
- **Sleep**: Sau 15 phút không dùng, service sẽ sleep
- **Cold start**: Request đầu tiên có thể mất 30-60 giây

### Nếu gặp lỗi "Out of Memory":

**Option 1**: Nâng cấp lên Starter plan ($7/tháng)
- 512MB RAM → unlimited
- Không sleep
- Deploy nhanh hơn

**Option 2**: Dùng Hugging Face Spaces (KHUYẾN NGHỊ)
- 16GB RAM miễn phí
- Không giới hạn
- Không sleep
- Xem file `DEPLOY_HUGGINGFACE.md` để biết cách deploy

## Troubleshooting

### Build failed:
```
Error: Killed
```
→ Out of memory khi build. Cần nâng cấp plan.

### API chậm:
- Request đầu tiên mất 30-60s vì cold start
- Các request sau sẽ nhanh hơn
- Nếu app không dùng >15 phút, service sleep lại

### Cannot push to GitHub:
```
fatal: Authentication failed
```
→ Cần tạo Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Chọn scopes: `repo`
4. Copy token và dùng làm password khi push

## Kiểm tra Logs

Nếu có lỗi, xem logs trên Render:
1. Vào dashboard
2. Click vào service `cropwise-api`
3. Tab **Logs** để xem chi tiết

## API Endpoints

- `GET /`: Status check
- `POST /predict`: Upload ảnh để phân tích (multipart/form-data)
- `GET /docs`: Swagger API documentation

---

✅ Sau khi hoàn thành các bước trên, app của bạn sẽ hoạt động mà không cần chạy localhost!
