# CropWise API - Corn Disease Detection

API for detecting corn leaf diseases using YOLO (leaf detection) + DenseNet121 (disease classification).

## Models
- **YOLO**: Detects and crops leaf regions from images
- **DenseNet121**: Classifies 7 corn diseases from cropped leaves

## Diseases Detected
1. Blight (Bệnh Khô Lá)
2. Common Rust (Bệnh Gỉ Sắt)
3. Downy Mildew (Bệnh Sương Mai)
4. Gray Leaf Spot (Bệnh Đốm Lá Xám)
5. Healthy (Khỏe Mạnh)
6. MLN - Lethal Necrosis (MLN - Hoại tử)
7. MSV - Streak Virus (MSV - Virus vằn)

## API Endpoints
- `GET /`: Health check
- `POST /predict`: Single image prediction
- `POST /predict-batch`: Batch image prediction

## Deployment
This app is designed to run on Hugging Face Spaces with Gradio interface.
