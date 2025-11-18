import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms
import torch.nn.functional as F
import numpy as np
from ultralytics import YOLO
from collections import OrderedDict

# Khởi tạo device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔧 Đang sử dụng thiết bị: {device}")

# Load YOLO model cho leaf detection
try:
    yolo_model = YOLO("yolo_leaf_model.pt")
    yolo_model.overrides['verbose'] = False
    print("✅ Đã load YOLO model thành công!")
except Exception as e:
    print(f"❌ Không thể load yolo_leaf_model.pt: {e}")
    raise

# Load model DenseNet121 for 7 classes
model = models.densenet121(pretrained=False)
num_ftrs = model.classifier.in_features
model.classifier = nn.Linear(num_ftrs, 7)

# Load trọng số
try:
    checkpoint = torch.load("model.pth", map_location=device)
    if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
        state_dict = checkpoint['state_dict']
    else:
        state_dict = checkpoint

    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        new_key = k.replace('module.', '') if k.startswith('module.') else k
        new_state_dict[new_key] = v

    try:
        model.load_state_dict(new_state_dict)
    except RuntimeError:
        model.load_state_dict(new_state_dict, strict=False)

    model = model.to(device)
    model.eval()
    print("✅ Đã load model thành công!")
except Exception as e:
    print(f"❌ Không thể load model.pth: {e}")
    raise

# Labels
labels_vi = {
    0: 'Bệnh Khô Lá',
    1: 'Bệnh Gỉ Sắt',
    2: 'Bệnh Sương Mai',
    3: 'Bệnh Đốm Lá Xám',
    4: 'Khỏe Mạnh',
    5: 'MLN - Hoại tử (MLN)',
    6: 'MSV - Virus vằn'
}

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

# Tiền xử lý ảnh
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def predict_disease(image):
    """Dự đoán bệnh từ ảnh"""
    try:
        if image is None:
            return "❌ Vui lòng tải lên một ảnh", None, ""
        
        # Convert to numpy array
        img_np = np.array(image)
        
        # YOLO detect và crop lá
        yolo_results = yolo_model.predict(
            source=img_np, 
            save=False, 
            verbose=False,
            imgsz=640,
            conf=0.25,
            device='cpu'
        )
        
        # Kiểm tra detection
        if len(yolo_results) == 0 or len(yolo_results[0].boxes) == 0:
            return "❌ Không phát hiện được lá trong ảnh. Vui lòng thử ảnh khác.", image, ""
        
        # Lấy bounding box đầu tiên
        boxes = yolo_results[0].boxes
        box = boxes[0]
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        
        # Crop ảnh lá
        cropped_img = img_np[y1:y2, x1:x2]
        cropped_pil = Image.fromarray(cropped_img)
        
        # Tiền xử lý cho DenseNet
        input_tensor = transform(cropped_pil).unsqueeze(0).to(device)
        
        # Dự đoán
        with torch.no_grad():
            output = model(input_tensor)
            probs = F.softmax(output, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0][pred_class].item()
        
        # Tạo kết quả
        info = disease_info[pred_class]
        result_text = f"""
### 🌿 Kết quả phân tích

**Chẩn đoán:** {info['name']}  
**Độ tin cậy:** {confidence*100:.2f}%

**📝 Mô tả:**  
{info['description']}

**💊 Cách xử lý:**  
{info['treatment']}
"""
        
        # Vẽ bounding box lên ảnh gốc
        img_with_box = image.copy()
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img_with_box)
        draw.rectangle([x1, y1, x2, y2], outline="green", width=3)
        
        return result_text, img_with_box, cropped_pil
        
    except Exception as e:
        return f"❌ Lỗi: {str(e)}", image, None

# Tạo Gradio interface
with gr.Blocks(title="CropWise - Phát hiện bệnh lúa mì") as demo:
    gr.Markdown("# 🌾 CropWise - Hệ thống Phát hiện Bệnh Ngô")
    gr.Markdown("Tải lên ảnh lá ngô để phát hiện bệnh tự động")
    
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="pil", label="📸 Tải ảnh lên")
            predict_btn = gr.Button("🔍 Phân tích", variant="primary")
        
        with gr.Column():
            output_text = gr.Markdown(label="Kết quả")
            output_image = gr.Image(type="pil", label="Ảnh với vùng lá được phát hiện")
            cropped_image = gr.Image(type="pil", label="Lá đã crop")
    
    predict_btn.click(
        fn=predict_disease,
        inputs=input_image,
        outputs=[output_text, output_image, cropped_image]
    )
    
    gr.Markdown("---")
    gr.Markdown("### 📱 API Endpoint cho Mobile App")
    gr.Markdown("Sử dụng URL: `https://your-space-name.hf.space/predict` để gọi từ React Native/Expo")

# Tạo FastAPI app cho API endpoint
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def api_predict(file: bytes):
    """API endpoint cho mobile app"""
    try:
        import io
        image = Image.open(io.BytesIO(file)).convert("RGB")
        img_np = np.array(image)
        
        # YOLO detect
        yolo_results = yolo_model.predict(
            source=img_np, 
            save=False, 
            verbose=False,
            imgsz=640,
            conf=0.25,
            device='cpu'
        )
        
        if len(yolo_results) == 0 or len(yolo_results[0].boxes) == 0:
            return {
                "success": False,
                "error": "Không phát hiện được lá trong ảnh."
            }
        
        boxes = yolo_results[0].boxes
        box = boxes[0]
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        
        cropped_img = img_np[y1:y2, x1:x2]
        cropped_pil = Image.fromarray(cropped_img)
        
        input_tensor = transform(cropped_pil).unsqueeze(0).to(device)
        
        with torch.no_grad():
            output = model(input_tensor)
            probs = F.softmax(output, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0][pred_class].item()
        
        all_predictions = {}
        for i in range(7):
            all_predictions[labels_vi.get(i, str(i))] = {
                "probability": float(probs[0][i] * 100)
            }
        
        return {
            "success": True,
            "leaf_detected": True,
            "leaf_bbox": [int(x1), int(y1), int(x2), int(y2)],
            "predicted_class_vi": labels_vi[pred_class],
            "confidence": float(confidence * 100),
            "disease_info": disease_info[pred_class],
            "all_predictions": all_predictions
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Mount Gradio app vào FastAPI
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
