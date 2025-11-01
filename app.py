from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms
import torch.nn.functional as F
import io
import uvicorn

app = FastAPI()

# Cho phép CORS để React Native có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔧 Đang sử dụng thiết bị: {device}")

# Load model ResNet18
model = models.resnet18(pretrained=False)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 4)  # 4 lớp bệnh

# Load trọng số đã train
model.load_state_dict(torch.load("model.pth", map_location=device))
model = model.to(device)
model.eval()

print("✅ Đã load model thành công!")

# Định nghĩa labels (giống trong notebook)
labels = {
    0: 'Blight',
    1: 'Common_Rust', 
    2: 'Gray_Leaf_Spot',
    3: 'Healthy'
}

# Định nghĩa labels tiếng Việt
labels_vi = {
    0: 'Bệnh Khô Lá',
    1: 'Bệnh Gỉ Sắt',
    2: 'Bệnh Đốm Lá Xám',
    3: 'Khỏe Mạnh'
}

# Mô tả bệnh
disease_info = {
    0: {
        'name': 'Bệnh Khô Lá (Blight)',
        'description': 'Bệnh do nấm gây ra, làm lá khô héo và chết dần.',
        'treatment': 'Sử dụng thuốc diệt nấm, cải thiện thoát nước, loại bỏ lá bệnh.'
    },
    1: {
        'name': 'Bệnh Gỉ Sắt (Common Rust)',
        'description': 'Bệnh nấm gây ra các đốm màu vàng cam trên lá.',
        'treatment': 'Phun thuốc diệt nấm chứa mancozeb hoặc chlorothalonil.'
    },
    2: {
        'name': 'Bệnh Đốm Lá Xám (Gray Leaf Spot)',
        'description': 'Bệnh nấm gây ra các vết đốm xám trên lá ngô.',
        'treatment': 'Luân canh cây trồng, sử dụng giống kháng bệnh, phun thuốc diệt nấm.'
    },
    3: {
        'name': 'Khỏe Mạnh (Healthy)',
        'description': 'Cây ngô hoàn toàn khỏe mạnh, không có dấu hiệu bệnh tật.',
        'treatment': 'Tiếp tục chăm sóc và theo dõi định kỳ.'
    }
}

# Tiền xử lý ảnh (giống trong notebook)
transform = transforms.Compose([
    transforms.Resize((256, 256)),  # Kích thước giống lúc train
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

@app.get("/")
async def root():
    return {
        "message": "CropWise - Corn Disease Detection API",
        "status": "running",
        "model": "ResNet18",
        "classes": labels_vi
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Đọc ảnh từ upload
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Tiền xử lý ảnh
        input_tensor = transform(image).unsqueeze(0).to(device)
        
        # Dự đoán
        with torch.no_grad():
            output = model(input_tensor)
            probs = F.softmax(output, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0][pred_class].item()
        
        # Tạo kết quả chi tiết
        all_predictions = {}
        for i in range(4):
            all_predictions[labels_vi[i]] = {
                "probability": float(probs[0][i] * 100),
                "label_en": labels[i]
            }
        
        # Trả về kết quả
        result = {
            "success": True,
            "predicted_class": labels[pred_class],
            "predicted_class_vi": labels_vi[pred_class],
            "confidence": float(confidence * 100),
            "disease_info": disease_info[pred_class],
            "all_predictions": all_predictions
        }
        
        print(f"✅ Dự đoán: {labels_vi[pred_class]} ({confidence*100:.2f}%)")
        
        return result
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print("🚀 Starting CropWise API Server...")
    print("📡 API sẽ chạy tại: http://localhost:8001")
    print("📖 Docs tại: http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)
