import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

class PoseDataset(Dataset):
    def __init__(self, dataset_path):
        dataset = np.load(dataset_path, allow_pickle=True).item()
        
        self.data = dataset['data']  # List of numpy arrays (num_frames, 33, 3)
        self.labels = dataset['labels']  # List of labels (strings like "A", "B", etc.)

        # Convert labels to numeric class indices
        self.label_map = {label: idx for idx, label in enumerate(sorted(set(self.labels)))}
        self.numeric_labels = [self.label_map[label] for label in self.labels]

        # Convert to tensor & reshape to (num_samples, 3, 100, 33)
        self.data = [torch.tensor(sample, dtype=torch.float32).permute(2, 0, 1) for sample in self.data]  
        self.labels = torch.tensor(self.numeric_labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

import numpy as np
from collections import Counter

dataset_path = "pose_dataset_interpolated.npy"

# Load dataset
dataset = np.load(dataset_path, allow_pickle=True).item()

# Extract data and labels
data = dataset['data']
labels = dataset['labels']

# Check dataset size
print(f"Total Samples: {len(data)}")

# Count occurrences of each label
label_counts = Counter(labels)
print("Label Distribution:")
for label, count in label_counts.items():
    print(f"{label}: {count} occurrences")

# Print shapes of each sample
for i, sample in enumerate(data[:5]):  # Print only first 5 to avoid long output
    print(f"Sample {i}: Shape {sample.shape}, Label: {labels[i]}")
