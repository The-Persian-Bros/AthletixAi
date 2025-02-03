import pyrealsense2 as rs
import cv2
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

#Create Pos marker - wget https://path-to-model/pose_landmarker.task -O pose_landmarker.task
base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True
)
detector = vision.PoseLandmarker.create_from_options(options)



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
    
    
    h,w,_ = annotated_image.shape
    landmark_Coordinates: dict = {i: (int(landmark.x * w), int(landmark.y * h)) for i,landmark in enumerate (pose_landmarks)}

    # print(landmark_Coordinates)
    return annotated_image, landmark_Coordinates


def process_and_save(imageArray, detector):
    #change input here
    imageCreator = mp.Image
    mpImage = imageCreator(mp.ImageFormat.SRGB, imageArray)

    detection_result = detector.detect(mpImage)

    #could speed things up here posible
    annotated_image,landmark_Coordinates = draw_landmarks_on_image(mpImage.numpy_view(), detection_result)


    return annotated_image, landmark_Coordinates


# Configure the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()

# Enable depth and color streams
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)
# config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)

pipeline.start(config)


#Setup open CV Graph Canvas
width, height = 700, 940
canvas = np.ones((height, width, 3), dtype=np.uint8) * 255



try:
    while True:
        # Wait for the next frame
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        # depth_frame = frames.get_depth_frame()

        # Convert images to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        # depth_image = np.asanyarray(depth_frame.get_data())


        #alter images 
        annotated_image, landmark_Coordinates = process_and_save(color_image, detector)

        cv2.imshow("Color Stream", annotated_image)

        # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # cv2.imshow("Depth Stream", depth_colormap)




        # Change Graph
        points =[]

        #update points
        points = landmark_Coordinates


        canvas = np.ones((height, width, 3), dtype=np.uint8) * 255  # Clear canvas
    
        # Draw axes
        cv2.line(canvas, (50, height - 50), (width - 50, height - 50), (0, 0, 0), 2)  # X-axis
        cv2.line(canvas, (50, height - 50), (50, 50), (0, 0, 0), 2)  # Y-axis

        # Plot points
        if(points!= None):
            for i in range(1, len(points)):
                cv2.circle(canvas, points[i], 3, (0, 0, 255), -1)

        # Show the updated image
        cv2.imshow("Real-Time Graph", canvas)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()


