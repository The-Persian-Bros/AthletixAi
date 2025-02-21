import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

class ClipComparisonVisualizer:
    def __init__(self, original_dataset_path="pose_dataset.npy", interpolated_dataset_path="pose_dataset_interpolated.npy", keypoint_indices=None, image_shape=(720, 1280)):
        """Loads the original and interpolated datasets."""
        self.original_dataset = np.load(original_dataset_path, allow_pickle=True).item()
        self.interpolated_dataset = np.load(interpolated_dataset_path, allow_pickle=True).item()
        
        self.original_data = self.original_dataset['data']
        self.interpolated_data = self.interpolated_dataset['data']
        
        self.keypoint_indices = keypoint_indices if keypoint_indices else list(range(self.original_data[0].shape[1]))  # All keypoints
        
        self.h, self.w = image_shape  # Image dimensions to scale keypoints
    
    def find_largest_clip(self):
        """Finds the largest clip in the original dataset."""
        largest_idx = np.argmax([clip.shape[0] for clip in self.original_data])
        return self.original_data[largest_idx], self.interpolated_data[largest_idx]

    def visualize_comparison_video(self, save_path="EstimatingHumanPos_PCHIP/comparison.gif"):
        """Creates an animation comparing the original and interpolated keypoints for each frame over a predetermined interval."""
        original_clip, interpolated_clip = self.find_largest_clip()
        num_frames_original = original_clip.shape[0]
        num_frames_interpolated = interpolated_clip.shape[0]
        
        frame_indices_interpolated = np.linspace(0, num_frames_interpolated - 1, num_frames_original).astype(int)
        
        fig, ax = plt.subplots(figsize=(8, 16))  # Increase figure size for a larger person representation
        ax.set_xlim(0, self.w)
        ax.set_ylim(self.h, 0)  # Flip y-axis for correct visualization
        ax.set_title("Original (Blue) vs Interpolated (Red) Keypoints")
        
        original_scatter = ax.scatter([], [], color='blue', label='Original', s=150)  # Increase size
        interpolated_scatter = ax.scatter([], [], color='red', label='Interpolated', s=150)
        ax.legend()

        def update(frame):
            original_points = original_clip[frame, self.keypoint_indices, :2]
            original_points[:, 0] = original_points[:, 0] * self.w + 100  # Scale x to image width and shift right
            original_points[:, 1] = original_points[:, 1] * self.h * 1.2  # Scale y to image height and enlarge
            
            interpolated_frame = frame_indices_interpolated[frame]
            interpolated_points = interpolated_clip[interpolated_frame, self.keypoint_indices, :2]
            interpolated_points[:, 0] = interpolated_points[:, 0] * self.w + 100  # Scale x to image width and shift right
            interpolated_points[:, 1] = interpolated_points[:, 1] * self.h * 1.2  # Scale y to image height and enlarge
            
            original_scatter.set_offsets(original_points)
            interpolated_scatter.set_offsets(interpolated_points)
            return original_scatter, interpolated_scatter

        ani = animation.FuncAnimation(fig, update, frames=num_frames_original, interval=100, blit=False)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        ani.save(save_path, writer='pillow', fps=10)
        plt.show()

# Usage Example
visualizer = ClipComparisonVisualizer(image_shape=(720, 1280))  # Example image size
visualizer.visualize_comparison_video()
