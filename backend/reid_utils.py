import torch
import torchvision.transforms as T
import torchvision.models as models
import numpy as np
import cv2
from PIL import Image

class ReIDExtractor:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # Using ResNet50 for feature extraction (standard backbone)
        # In a real heavy production app, we would use osnet_x1_0
        self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        
        # Remove the classification layer (fc) to get embeddings
        self.model = torch.nn.Sequential(*(list(self.model.children())[:-1]))
        
        self.model.to(self.device)
        self.model.eval()
        
        self.transform = T.Compose([
            T.Resize((256, 128)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def extract(self, img_numpy):
        """Extracts feature vector from a numpy image (BGR)."""
        if img_numpy is None or img_numpy.size == 0:
            return np.zeros((2048,))
        
        # Convert BGR (OpenCV) to RGB (PIL)
        img = cv2.cvtColor(img_numpy, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        
        input_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.model(input_tensor)
            
        return features.cpu().numpy().flatten()

def compare_embeddings(emb1, emb2):
    """Computes Cosine Similarity between two embeddings."""
    if emb1 is None or emb2 is None:
        return 0.0
    
    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return np.dot(emb1, emb2) / (norm1 * norm2)
