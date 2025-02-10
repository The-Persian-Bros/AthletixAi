import numpy as np
from scipy.interpolate import PchipInterpolator

class PCHIPInterpolator:
    def __init__(self, dataset_path, target_frames=100):
        self.dataset_path = dataset_path
        self.target_frames = target_frames
        self.dataset = self.load_dataset()
        self.interpolated_data = []
        self.interpolated_labels = []
    
    def load_dataset(self):
        """Loads the dataset from a .npy file."""
        try:
            return np.load(self.dataset_path, allow_pickle=True).item()
        except FileNotFoundError:
            print(f"Dataset not found at {self.dataset_path}")
            return None
    
    def interpolate_sample(self, sample):
        """Interpolates a single sample using PCHIP to reach target_frames."""
        original_length = sample.shape[0]
        
        if original_length < 2:
            return np.repeat(sample, self.target_frames, axis=0)

        x_old = np.linspace(0, 1, original_length)
        x_new = np.linspace(0, 1, self.target_frames)

        # Interpolating each keypoint & coordinate (X, Y, Z) separately
        interpolated_sample = np.array([
            PchipInterpolator(x_old, sample[:, keypoint, coord])(x_new)
            for keypoint in range(sample.shape[1])  # Loop over keypoints
            for coord in range(sample.shape[2])     # Loop over (X, Y, Z)
        ]).T.reshape(self.target_frames, sample.shape[1], sample.shape[2])  # Reshape back

        return interpolated_sample
    
    def process_dataset(self):
        """Processes the dataset, applying PCHIP interpolation to clips below 100 frames."""
        if self.dataset is None:
            return
        
        for sample, label in zip(self.dataset['data'], self.dataset['labels']):
            if len(sample) < self.target_frames:
                interpolated_sample = self.interpolate_sample(sample)
            else:
                interpolated_sample = sample  # Keep original if already 100+ frames
            
            self.interpolated_data.append(interpolated_sample)
            self.interpolated_labels.append(label)
        
    def save_interpolated_dataset(self, output_path):
        """Saves the new dataset with interpolated sequences."""
        new_dataset = {'data': self.interpolated_data, 'labels': self.interpolated_labels}
        np.save(output_path, new_dataset)
        print(f"Interpolated dataset saved to {output_path}")