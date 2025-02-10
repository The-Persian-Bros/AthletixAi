import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

class PoseDataset(Dataset):
    def __init__(self, dataset_path):
        # Load the dataset
        dataset = np.load(dataset_path, allow_pickle=True).item()
        
        self.data = dataset['data']  # List of numpy arrays (num_frames, 33, 3)
        self.labels = dataset['labels']  # List of labels (strings like "A", "B", etc.)

        # Convert labels to numeric class indices
        self.label_map = {label: idx for idx, label in enumerate(sorted(set(self.labels)))}
        self.numeric_labels = [self.label_map[label] for label in self.labels]

        # Convert to tensor & reshape to match ST-GCN format: (num_samples, 33, num_frames, 3)
        self.data = [torch.tensor(np.array(sample), dtype=torch.float32).permute(1, 0, 2) for sample in self.data]
        self.labels = torch.tensor(self.numeric_labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

# Load dataset
dataset_path = "pose_dataset.npy"
train_dataset = PoseDataset(dataset_path)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

# Verify dataset
sample_data, sample_label = next(iter(train_loader))
print(f"Data shape: {sample_data.shape}, Labels shape: {sample_label.shape}")
