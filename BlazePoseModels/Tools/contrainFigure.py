import cv2
import mediapipe as mp
import numpy as np
import time

class NormalizedLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)
mp_drawing = mp.solutions.drawing_utils

# Start Video Capture
cap = cv2.VideoCapture(0)

prev_angle = None
prev_time = None

NEUTRAL_THRESHOLD = 0.05


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        h,w,_ = frame.shape

        normalizedLandmarks =[]
        for landmark in landmarks:
            normalizedLandmarks.append( NormalizedLandmark(int(landmark.x * w), int(landmark.y * h)) )

        if not normalizedLandmarks:
            normalizedLandmarks = []
        
        greatestX = -100000
        minimalX = 1000000
        greatestY = -100000
        minimalY = 100000


        for landmark in normalizedLandmarks:
            if landmark.x > greatestX:
                greatestX = landmark.x
            if landmark.x < minimalX:
                minimalX = landmark.x
            if landmark.y > greatestY:
                greatestY = landmark.y
            if landmark.y< minimalY:
                minimalY = landmark.y

        cv2.rectangle(frame, (minimalX, minimalY), (greatestX, greatestY), (255, 0, 0), 2)
        
        
        # Get 3D Z-coordinates for shoulders
        left_shoulder_z = landmarks[11].z
        right_shoulder_z = landmarks[12].z

        # Get X-coordinates (horizontal distance) for shoulders
        left_shoulder_x = landmarks[11].x
        right_shoulder_x = landmarks[12].x

        # Compute shoulder width (distance in X-coordinates)
        shoulder_width = abs(right_shoulder_x - left_shoulder_x)

        # Compute yaw angle using arctan
        if shoulder_width > 0:  # Avoid division by zero
            yaw_angle_rad = np.arctan((right_shoulder_z - left_shoulder_z) / shoulder_width)
            yaw_angle_deg = np.degrees(yaw_angle_rad)  # Convert to degrees
        else:
            yaw_angle_deg = 0  # No valid shoulder width detected

        # Display yaw angle on screen
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (0, 255, 0)  # Green
        thickness = 2

        # Display the values on screen
        cv2.putText(frame, f"Greatest X: {greatestX}", (30, 50), font, font_scale, color, thickness)
        cv2.putText(frame, f"Minimal X: {minimalX}", (30, 100), font, font_scale, color, thickness)
        cv2.putText(frame, f"Greatest Y: {greatestY}", (30, 150), font, font_scale, color, thickness)
        cv2.putText(frame, f"Minimal Y: {minimalY}", (30, 200), font, font_scale, color, thickness)


        cv2.putText(frame, f"Yaw Angle: {yaw_angle_deg:.2f} deg", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        # Draw landmarks
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Show frame
    cv2.imshow("Spin Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
