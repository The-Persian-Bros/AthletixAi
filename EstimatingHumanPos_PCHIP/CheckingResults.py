import numpy as np
import matplotlib.pyplot as plt

class ClipComparisonVisualizer:
    def __init__(self, original_dataset_path="pose_dataset.npy", interpolated_dataset_path="pose_dataset_interpolated.npy", keypoint_indices=None):
        """Loads the original and interpolated datasets."""
        self.original_dataset = np.load(original_dataset_path, allow_pickle=True).item()
        self.interpolated_dataset = np.load(interpolated_dataset_path, allow_pickle=True).item()
        
        self.original_data = self.original_dataset['data']
        self.interpolated_data = self.interpolated_dataset['data']
        
        self.keypoint_indices = keypoint_indices if keypoint_indices else [0, 1, 2, 3]  # Default: First 4 keypoints

    def find_largest_clip(self):
        """Finds the largest clip in the original dataset."""
        largest_idx = np.argmax([clip.shape[0] for clip in self.original_data])
        return self.original_data[largest_idx], self.interpolated_data[largest_idx]

    def visualize_comparison(self):
        """Displays the original vs interpolated keypoints' X-values over time."""
        original_clip, interpolated_clip = self.find_largest_clip()

        num_frames_original = original_clip.shape[0]
        num_frames_interpolated = interpolated_clip.shape[0]

        x_values_original = original_clip[:, self.keypoint_indices, 0]  # X values of selected keypoints
        x_values_interpolated = interpolated_clip[:, self.keypoint_indices, 0]

        frame_indices_original = np.arange(num_frames_original)
        frame_indices_interpolated = np.linspace(0, num_frames_original - 1, num_frames_interpolated)

        plt.figure(figsize=(14, 6))
        for i, keypoint_index in enumerate(self.keypoint_indices):
            plt.plot(frame_indices_original, x_values_original[:, i], 'bo-', label=f'Original Keypoint {keypoint_index}' if i == 0 else "")
            plt.plot(frame_indices_interpolated, x_values_interpolated[:, i], 'ro-', label=f'Interpolated Keypoint {keypoint_index}' if i == 0 else "")

        plt.xlabel("Frame Index")
        plt.ylabel("X Position")
        plt.title("Original vs Interpolated X-Values Timeline")
        plt.legend()
        plt.grid()
        plt.show()

# Usage Example
visualizer = ClipComparisonVisualizer(keypoint_indices=[8, 3, 5])  # Choose keypoints to display
visualizer.visualize_comparison()
