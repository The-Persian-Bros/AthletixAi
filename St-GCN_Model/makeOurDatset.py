import torch
from torch.utils.data import Dataset
import cv2
import numpy as np
import mediapipe as mp
import os
from PCHIP_Interploator import PCHIPInterpolator

video_path = "Videos/Input/tennisPlayer_badView.mp4"

# Button Positions (X1, Y1, X2, Y2) - Adjusted for separate window
BUTTONS = {
    "PAUSE": (50, 50, 350, 150),
    "OverServe": (50, 200, 350, 300),
    "UnderServe": (400, 200, 700, 300),
    "C": (50, 350, 350, 450),
    "D": (400, 350, 700, 450),
    "E": (50, 500, 350, 600),
}

# Variables
paused = False
segment_data = []
dataset_data = []
dataset_labels = []
prev_frame = None  # Store the last known frame for interpolation

# Initialize Mediapipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Create button window
button_window = np.ones((650, 800, 3), dtype=np.uint8) * 255  

def draw_buttons():
    """Draw buttons on the separate button window."""
    global button_window
    button_window.fill(255)  # Reset to white background
    
    for text, (x1, y1, x2, y2) in BUTTONS.items():
        color = (0, 0, 255) if text == "PAUSE" and paused else (255, 0, 0)
        cv2.rectangle(button_window, (x1, y1), (x2, y2), color, -1)
        cv2.putText(button_window, text, (x1 + 60, y1 + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow("Buttons", button_window)

def check_button_click(x, y, window_name):
    """Handles button clicks in the separate window."""
    global paused, segment_data, dataset_data, dataset_labels

    if window_name == "Buttons":
        for text, (x1, y1, x2, y2) in BUTTONS.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                if text == "PAUSE":
                    paused = not paused
                else:
                    if len(segment_data) > 0:
                        dataset_data.append(np.array(segment_data))
                        dataset_labels.append(text)
                        print(f"Segment with {len(segment_data)} frames saved with label: {text}")
                        segment_data = []  # Reset segment
                return

def extract_keypoints(results):
    """Extracts 33 pose keypoints, ensuring all frames have complete data."""
    global prev_frame
    keypoints = np.zeros((33, 3)) if prev_frame is None else prev_frame.copy()
    visible_count = 0

    if results.pose_landmarks:
        for i, lm in enumerate(results.pose_landmarks.landmark):
            if i < 33:
                keypoints[i] = [lm.x, lm.y, lm.z]
                if lm.visibility > 0.5:  # Only count keypoints with high confidence
                    visible_count += 1

    # Skip frame if too many keypoints are missing
    if visible_count < 20:  
        return None  

    prev_frame = keypoints  # Save for next frame interpolation
    return keypoints

def mouse_callback(event, x, y, flags, param):
    """Handles mouse click events."""
    if event == cv2.EVENT_LBUTTONDOWN:
        check_button_click(x, y, "Buttons")

def main():
    global paused, segment_data

    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file!")
        return

    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Scale down while maintaining aspect ratio
    max_height = 900
    scale_factor = min(1.0, max_height / original_height)
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)

    cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Video", new_width, new_height)

    cv2.namedWindow("Buttons", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Buttons", 800, 650)
    cv2.setMouseCallback("Buttons", mouse_callback)

    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print("End of video")
                    break

                # Convert to RGB
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_rgb.flags.writeable = False
                results = pose.process(image_rgb)
                image_rgb.flags.writeable = True

                # Draw keypoints
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Extract keypoints & add to dataset if valid
                keypoints = extract_keypoints(results)
                if keypoints is not None:
                    segment_data.append(keypoints)

            # Draw buttons in separate window
            draw_buttons()
            cv2.imshow("Video", frame)

            # Quit on 'q'
            if cv2.waitKey(200) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    # Save dataset
    dataset = {'data': dataset_data, 'labels': dataset_labels}
    np.save("pose_dataset.npy", dataset)
    print("Dataset saved as pose_dataset.npy")

if __name__ == "__main__":
    main()
    interpolator = PCHIPInterpolator("pose_dataset.npy")
    interpolator.process_dataset()
    interpolator.save_interpolated_dataset("pose_dataset_interpolated.npy")
