import torch
from torch.utils.data import Dataset
import cv2
import numpy as np
import mediapipe as mp
import os
from PCHIP_Interploator import PCHIPInterpolator

video_path = "Videos\Input\Ryan.mp4"

# Button Positions (X1, Y1, X2, Y2)
BUTTONS = {
    "PAUSE": (50, 50, 350, 150),
    "OverServe": (50, 200, 350, 300),
    "UnderServe": (400, 200, 700, 300),
    "C": (50, 350, 350, 450),
    "D": (400, 350, 700, 450),
    "E": (50, 500, 350, 600),
}

# Default state
paused = False
current_label = None  # Active label while holding button
segment_data = []
dataset_data = []
dataset_labels = []
prev_frame = None  # Store last known frame for interpolation
frame_count = 0  # Track frames within the current 60-frame segment
segment_label = None  # Stores label for the current segment

# Initialize Mediapipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Create button window
button_window = np.ones((700, 800, 3), dtype=np.uint8) * 255  

def draw_buttons():
    """Draw buttons and progress bar on the button window."""
    global button_window, frame_count
    
    button_window.fill(255)  # Reset to white background
    
    for text, (x1, y1, x2, y2) in BUTTONS.items():
        if text == "PAUSE":
            color = (0, 0, 255) if paused else (255, 0, 0)
        else:
            color = (0, 255, 0) if text == current_label else (255, 0, 0)
        
        cv2.rectangle(button_window, (x1, y1), (x2, y2), color, -1)
        cv2.putText(button_window, text, (x1 + 60, y1 + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Draw progress bar (slider)
    progress_x = int((frame_count / 60) * 750)  # Scales to window width
    cv2.rectangle(button_window, (25, 650), (progress_x + 25, 680), (0, 0, 255), -1)  # Red progress bar
    cv2.rectangle(button_window, (25, 650), (775, 680), (0, 0, 0), 2)  # Border
    
    cv2.imshow("Buttons", button_window)

def check_button_status(x, y, event_type):
    """Handles button press and release events."""
    global paused, current_label, segment_label

    for text, (x1, y1, x2, y2) in BUTTONS.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            if text == "PAUSE":
                if event_type == cv2.EVENT_LBUTTONDOWN:
                    paused = not paused
            else:
                if event_type == cv2.EVENT_LBUTTONDOWN:
                    current_label = text
                    segment_label = text  # Assign segment label
                elif event_type == cv2.EVENT_LBUTTONUP:
                    current_label = None  # Reset label on release
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
    """Handles mouse click and release events."""
    if event in [cv2.EVENT_LBUTTONDOWN, cv2.EVENT_LBUTTONUP]:
        check_button_status(x, y, event)

def main():
    global paused, segment_data, frame_count, segment_label

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
    cv2.resizeWindow("Buttons", 800, 700)
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

                frame_count += 1

                # When 60 frames are reached, store the segment
                if frame_count == 60:
                    dataset_data.append(np.array(segment_data))
                    dataset_labels.append(segment_label if segment_label else "None")  # Assign stored label
                    segment_data = []  # Reset for next 60 frames
                    frame_count = 0  # Reset frame counter
                    segment_label = None  # Reset label for new clip

            # Draw buttons and progress bar
            draw_buttons()
            cv2.imshow("Video", frame)

            # Quit on 'q'
            if cv2.waitKey(50) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    # Save dataset
    dataset = {'data': dataset_data, 'labels': dataset_labels}
    np.save("pose_dataset.npy", dataset)
    print("Dataset saved as pose_dataset.npy")

if __name__ == "__main__":
    main()
    interpolator = PCHIPInterpolator("pose_dataset.npy", 200)
    interpolator.process_dataset()
    interpolator.save_interpolated_dataset("pose_dataset_interpolated.npy")
