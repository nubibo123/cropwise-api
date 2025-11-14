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


# Load model DenseNet121 for 7 classes
model = models.densenet121(pretrained=False)
num_ftrs = model.classifier.in_features
model.classifier = nn.Linear(num_ftrs, 7)  # 7 lớp bệnh

# Load trọng số đã train (robust loading)
from collections import OrderedDict
try:
    checkpoint = torch.load("model.pth", map_location=device)
    # If checkpoint is a dict with 'state_dict' key (training checkpoint), extract it
    if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
        state_dict = checkpoint['state_dict']
    else:
        state_dict = checkpoint

    # Remove module. prefix if the model was saved from DataParallel
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        new_key = k.replace('module.', '') if k.startswith('module.') else k
        new_state_dict[new_key] = v


    try:
        model.load_state_dict(new_state_dict)
    except RuntimeError:
        # Last resort: try non-strict loading to allow partial matches
        model.load_state_dict(new_state_dict, strict=False)

    model = model.to(device)
    model.eval()
    print("✅ Đã load model thành công!")
except Exception as e:
    print(f"❌ Không thể load model.pth: {e}")
    raise


# Định nghĩa labels (the model uses 7 classes; mapping index -> english label)
labels = {
    0: 'Blight',
    1: 'Common_Rust',
    2: 'Downy_Mildew',
    3: 'Gray_Leaf_Spot',
    4: 'Healthy',
    5: 'MLN_Lethal_Necrosis',
    6: 'MSV_Streak_Virus'
}

# Định nghĩa labels tiếng Việt (index -> vietnamese label)
labels_vi = {
    0: 'Bệnh Khô Lá',
    1: 'Bệnh Gỉ Sắt',
    2: 'Bệnh Sương Mai',
    3: 'Bệnh Đốm Lá Xám',
    4: 'Khỏe Mạnh',
    5: 'MLN - Hoại tử (MLN)',
    6: 'MSV - Virus vằn'
}

# Mô tả bệnh (sơ lược) cho 7 lớp
disease_info = {
    0: {
        'name': 'Bệnh Khô Lá (Blight)',
        'description': 'Bệnh do nấm gây ra, làm lá khô héo và chết dần.',
        'treatment': 'Sử dụng thuốc diệt nấm, cải thiện thoát nước, loại bỏ lá bệnh.'
    },
    1: {
        'name': 'Bệnh Gỉ Sắt (Common Rust)',
        'description': 'Xuất hiện các đốm màu vàng-cam trên lá, do nấm gây ra.',
        'treatment': 'Phun thuốc diệt nấm phù hợp và quản lý đồng ruộng.'
    },
    2: {
        'name': 'Bệnh Sương Mai (Downy Mildew)',
        'description': 'Bệnh do nấm mốc gây ra, lá có lớp bột trắng ở mặt dưới.',
        'treatment': 'Cải thiện thông gió, tránh ẩm ướt, sử dụng giống kháng và hóa chất khi cần.'
    },
    3: {
        'name': 'Bệnh Đốm Lá Xám (Gray Leaf Spot)',
        'description': 'Vết đốm xám trên lá, làm giảm diện tích quang hợp.',
        'treatment': 'Luân canh cây trồng, sử dụng giống kháng bệnh, phun thuốc khi cần.'
    },
    4: {
        'name': 'Khỏe Mạnh (Healthy)',
        'description': 'Cây ngô hoàn toàn khỏe mạnh, không có dấu hiệu bệnh.',
        'treatment': 'Tiếp tục chăm sóc và theo dõi định kỳ.'
    },
    5: {
        'name': 'MLN - Hoại tử (MLN Lethal Necrosis)',
        'description': 'Hội chứng nghiêm trọng do kết hợp virus, gây hoại tử và chết cây.',
        'treatment': 'Sử dụng giống kháng, quản lý vector (côn trùng), và biện pháp quản lý dịch hại tích hợp.'
    },
    6: {
        'name': 'MSV - Virus vằn (MSV Streak Virus)',
        'description': 'Virus gây sọc vằn trên lá, làm giảm năng suất.',
        'treatment': 'Quản lý côn trùng truyền bệnh, loại bỏ cây bệnh, sử dụng giống kháng.'
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
        "model": "DenseNet121",
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
        
        # Tạo kết quả chi tiết cho tất cả 7 lớp
        all_predictions = {}
        num_classes = output.shape[1]
        for i in range(num_classes):
            all_predictions[labels_vi.get(i, str(i))] = {
                "probability": float(probs[0][i] * 100),
                "label_en": labels.get(i, str(i))
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
