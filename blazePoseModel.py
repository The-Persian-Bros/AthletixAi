from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      solutions.pose.POSE_CONNECTIONS,
      solutions.drawing_styles.get_default_pose_landmarks_style())
  return annotated_image


#Create Pos marker - wget https://path-to-model/pose_landmarker.task -O pose_landmarker.task
base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True
)
detector = vision.PoseLandmarker.create_from_options(options)


import os
import cv2

output_dir = "Images/Output"
image_paths = ["Images\Input\Jumper.jpg"]

def process_and_save(image_path, detector, output_dir):
    image = mp.Image.create_from_file(image_path)



    detection_result = detector.detect(image)




    annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)
    
    # Save
    output_path = os.path.join(output_dir, os.path.basename(image_path))
    cv2.imwrite(output_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))  # Convert to BGR for saving
    print(f"Saved annotated image to: {output_path}")


for path in image_paths:
    process_and_save(path, detector, output_dir)
