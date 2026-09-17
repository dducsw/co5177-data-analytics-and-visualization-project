# Computer Vision: Best Practices & Reference Guide

## 1. Principles
- **Transfer Learning First**: Never train a vision model from scratch on small-to-medium datasets. Use proven pretrained backbones (`ResNet50`, `EfficientNet-B0`, `ConvNeXt-Tiny`, or `ViT-B/16`).
- **Data Augmentation is Free Regularization**: Random crops, horizontal flips, and moderate color jitter prevent overfitting without extra annotations.
- **Two-Phase Training**:
  - *Phase 1*: Freeze pretrained weights, train the new classification head for 2-3 epochs with standard learning rate (`1e-3`).
  - *Phase 2*: Unfreeze top backbone layers and fine-tune with a 10x-100x lower learning rate (`1e-5` to `3e-5`) with Cosine Annealing scheduler.

## 2. Standard PyTorch Pipeline
```python
import torch
import torch.nn as nn
from torchvision import models
import torchvision.transforms.v2 as T

train_transforms = T.Compose([
    T.ToImage(),
    T.RandomResizedCrop(size=(224, 224), scale=(0.8, 1.0)),
    T.RandomHorizontalFlip(p=0.5),
    T.ToDtype(torch.float32, scale=True),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load pretrained ResNet50
weights = models.ResNet50_Weights.DEFAULT
model = models.resnet50(weights=weights)

# Freeze backbone
for param in model.parameters():
    param.requires_grad = False

# Replace classifier head
model.fc = nn.Linear(model.fc.in_features, num_classes)
```

## 3. Diagnostics & Error Inspection
- Plot a 4x4 grid of misclassified images showing `True Label`, `Predicted Label`, and `Confidence Score`.
- Check if images with low confidence are blurry, poorly cropped, or ambiguous even to human eyes.
- Use Grad-CAM to ensure the model focuses on relevant objects rather than background shortcuts.
