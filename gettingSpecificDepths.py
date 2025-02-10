import cv2
import mediapipe as mp
import numpy as np
import time

class NormalizedLandmark:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
class Rect:
    def __init__(self, x1,x2,y1,y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

def createLandmarkList(frameShape, results):
    landmarks = results.pose_landmarks.landmark
    h,w,_ = frameShape

    normalizedLandmarks =[]
    for landmark in landmarks:
        normalizedLandmarks.append( NormalizedLandmark(int(landmark.x * w), int(landmark.y * h), landmark.z) )

    if not normalizedLandmarks:
        return []
    else:
        return normalizedLandmarks


def createBoundingBoxAroudnPerson(frame, landmarks):
    greatestX = -100000
    minimalX = 1000000
    greatestY = -100000
    minimalY = 100000

    for landmark in landmarks:
        if landmark.x > greatestX:
            greatestX = landmark.x
        if landmark.x < minimalX:
            minimalX = landmark.x
        if landmark.y > greatestY:
            greatestY = landmark.y
        if landmark.y< minimalY:
            minimalY = landmark.y

    cv2.rectangle(frame, (minimalX, minimalY), (greatestX, greatestY), (255, 0, 0), 2)
    return Rect(minimalX, greatestX, minimalY, greatestY)

def normalizeLandmarksToCVGraph(landmarks, rect):
    return [
            NormalizedLandmark(
                int((l.x - rect.x1) / (rect.x2 - rect.x1) * 625) +50,  # Normalize X
                int((l.y - rect.y1) / (rect.y2 - rect.y1) * 625)+50,
                l.z
            )
            for l in landmarks
        ]


def drawCvGraph(landmarkPoints):
    canvas = np.ones((height, width, 3), dtype=np.uint8) * 255  # Clear canvas
    
    # Draw axes
    cv2.line(canvas, (50, height - 50), (width - 50, height - 50), (0, 0, 0), 2)  # X-axis
    cv2.line(canvas, (50, height - 50), (50, 50), (0, 0, 0), 2)  # Y-axis

        # Plot points
    if(landmarkPoints!= None):
        for l in landmarkPoints:
            cv2.circle(canvas, (l.x, l.y), 5, (0, 255, 0), -1)
        
        # y= int(-landmarks[12].z *500)  + 450

        # cv2.line(canvas, (0,y), (700,y), (0,0,250))

    return canvas





# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)
mp_drawing = mp.solutions.drawing_utils

# Start Video Capture
cap = cv2.VideoCapture(0)

width, height = 900, 940
canvas = np.ones((height, width, 3), dtype=np.uint8) * 255




while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:

        
        h,w,_ = frame.shape

        landmarks = createLandmarkList(frame.shape, results)

        # boundingBox = createBoundingBoxAroudnPerson(frame,landmarks)

        graphCanvas = drawCvGraph(normalizeLandmarksToCVGraph(landmarks, Rect(0,w,0,h)))
        
        cv2.imshow("Real-Time Graph", graphCanvas)

        # Draw landmarks
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Show frame
    cv2.imshow("Spin Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
