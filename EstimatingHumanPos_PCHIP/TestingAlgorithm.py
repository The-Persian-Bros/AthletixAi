import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator

def interpolate_keypoints_pchip(sample, num_frames):
    """Interpolates keypoint sequences to a fixed number of frames using PCHIP."""
    original_length = sample.shape[0]
    x_old = np.linspace(0, 1, original_length)  # Original timestamps
    x_new = np.linspace(0, 1, num_frames)  # New timestamps

    # Apply PCHIP interpolation for each keypoint's (x, y, z) coordinates
    interpolated_sample = np.array([
        PchipInterpolator(x_old, sample[:, i])(x_new)  # PCHIP interpolation on each keypoint
        for i in range(sample.shape[1])  # Loop over keypoints (not 3, but based on data shape)
    ]).T  # Transpose back to (num_frames, num_keypoints)

    return interpolated_sample

# Create more chaotic motion data (3 keypoints, 45 frames)
num_frames_original = 45
t = np.linspace(0, 2 * np.pi, num_frames_original)  # Time from 0 to 2*pi for smooth motion

# Chaotic motion functions: Sin with random noise, Cos with random amplitude, and Sum of Sin and Cos
np.random.seed(42)  # Fixing seed for reproducibility

# Keypoint 1: Sin with random noise
keypoint1 = np.sin(t) + np.random.normal(0, 0.1, num_frames_original)

# Keypoint 2: Cos with random amplitude scaling
amplitude = np.random.uniform(0.8, 1.2)
keypoint2 = amplitude * np.cos(t) + np.random.normal(0, 0.1, num_frames_original)

# Keypoint 3: Sum of Sin and Cos with random phase shifts
phase_shift = np.random.uniform(0, np.pi)
keypoint3 = np.sin(t + phase_shift) + np.cos(t) + np.random.normal(0, 0.1, num_frames_original)

# Stack them into a (frames, keypoints) matrix
original_data = np.vstack([keypoint1, keypoint2, keypoint3]).T

# Interpolate to different frame sizes using PCHIP
interpolated_data_60 = interpolate_keypoints_pchip(original_data, 60)
interpolated_data_100 = interpolate_keypoints_pchip(original_data, 100)

# Calculate error between original and interpolated data (absolute difference)
def calculate_error(original_data, interpolated_data):
    return np.abs(original_data - interpolated_data)

error_60 = calculate_error(original_data, interpolated_data_60[:num_frames_original, :])  # Only compare first 45 frames
error_100 = calculate_error(original_data, interpolated_data_100[:num_frames_original, :])  # Only compare first 45 frames

# Calculate total error for each keypoint over time
total_error_60 = error_60.sum(axis=1)
total_error_100 = error_100.sum(axis=1)

# Plot original vs interpolated motion for each interpolation case and error over time
plt.figure(figsize=(12, 15))

# Plot for 60 frames interpolation
plt.subplot(4, 1, 1)
for i in range(3):  # Plot for 3 keypoints (X, Y, Z)
    # Plot both the original and the interpolated (60 frames) data for each keypoint
    plt.plot(np.linspace(0, 1, num_frames_original), original_data[:, i], 'bo-', label=f"Original (45 frames) - Keypoint {i+1}")
    plt.plot(np.linspace(0, 1, 60), interpolated_data_60[:, i], 'ro-', label=f"Interpolated (60 frames) - Keypoint {i+1}")
plt.xlabel("Normalized Time")
plt.ylabel("Position of Keypoints")
plt.title(f"Interpolation to 60 Frames (PCHIP) - Original vs Interpolated")
plt.legend()
plt.grid()

# Plot for 100 frames interpolation
plt.subplot(4, 1, 2)
for i in range(3):  # Plot for 3 keypoints (X, Y, Z)
    # Plot both the original and the interpolated (100 frames) data for each keypoint
    plt.plot(np.linspace(0, 1, num_frames_original), original_data[:, i], 'bo-', label=f"Original (45 frames) - Keypoint {i+1}")
    plt.plot(np.linspace(0, 1, 100), interpolated_data_100[:, i], 'ro-', label=f"Interpolated (100 frames) - Keypoint {i+1}")
plt.xlabel("Normalized Time")
plt.ylabel("Position of Keypoints")
plt.title(f"Interpolation to 100 Frames (PCHIP) - Original vs Interpolated")
plt.legend()
plt.grid()

# Plot error for 60 frames interpolation
plt.subplot(4, 1, 3)
plt.plot(np.linspace(0, 1, num_frames_original), total_error_60, 'bo-', label="Error (60 frames)")
plt.xlabel("Normalized Time")
plt.ylabel("Total Error (sum of keypoints)")
plt.title(f"Error Over Time (Interpolation to 60 Frames)")
plt.legend()
plt.grid()

# Plot error for 100 frames interpolation
plt.subplot(4, 1, 4)
plt.plot(np.linspace(0, 1, num_frames_original), total_error_100, 'bo-', label="Error (100 frames)")
plt.xlabel("Normalized Time")
plt.ylabel("Total Error (sum of keypoints)")
plt.title(f"Error Over Time (Interpolation to 100 Frames)")
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
