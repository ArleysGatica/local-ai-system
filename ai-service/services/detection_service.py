import io
import torch
import torchvision
from torchvision import transforms
from PIL import Image


class DetectionService:
    """Service for detecting objects in images using PyTorch Faster R-CNN."""
    
    # COCO dataset labels
    COCO_LABELS = [
        '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
        'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
        'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
        'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
        'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
        'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
        'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
        'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
        'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
        'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
        'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
    ]
    
    def __init__(self, confidence_threshold=0.5):
        """
        Initialize detection service with pre-trained Faster R-CNN model.
        
        Args:
            confidence_threshold: Minimum confidence score for detections (0-1)
        """
        self.confidence_threshold = confidence_threshold
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load pre-trained Faster R-CNN model
        print("Loading Faster R-CNN model...")
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
            weights=torchvision.models.detection.FasterRCNN_ResNet50_FPN_Weights.DEFAULT
        )
        self.model.to(self.device)
        self.model.eval()
        print(f"Model loaded on device: {self.device}")
        
        # Image transformation
        self.transform = transforms.Compose([
            transforms.ToTensor(),
        ])
    
    def detect_objects(self, image_bytes):
        """
        Detect objects in an image.
        
        Args:
            image_bytes: Image content as bytes
            
        Returns:
            dict: Detections with labels, scores, and bounding boxes
        """
        try:
            # Load and transform image
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_tensor = self.transform(image).to(self.device)
            
            # Perform detection
            with torch.no_grad():
                predictions = self.model([image_tensor])[0]
            
            # Filter detections by confidence threshold
            detections = []
            for i in range(len(predictions['boxes'])):
                score = predictions['scores'][i].item()
                
                if score >= self.confidence_threshold:
                    label_idx = predictions['labels'][i].item()
                    label = self.COCO_LABELS[label_idx] if label_idx < len(self.COCO_LABELS) else 'unknown'
                    
                    # Skip background and N/A labels
                    if label in ('__background__', 'N/A'):
                        continue
                    
                    bbox = predictions['boxes'][i].cpu().numpy().tolist()
                    
                    detections.append({
                        'label': label,
                        'score': round(score, 4),
                        'bbox': [round(coord, 2) for coord in bbox]  # [x1, y1, x2, y2]
                    })
            
            # Sort by confidence score (highest first)
            detections.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'success': True,
                'detections': detections,
                'totalDetections': len(detections),
                'imageSize': {
                    'width': image.width,
                    'height': image.height
                }
            }
            
        except Exception as e:
            raise Exception(f"Error detecting objects: {str(e)}")
