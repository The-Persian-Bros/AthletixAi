import cv2
import numpy as np
import random
import time

# Create a blank white canvas
width, height = 700, 940
canvas = np.ones((height, width, 3), dtype=np.uint8) * 255

# Initialize an empty list to store points
points = []

while True:
    
    # Append to list of points
    # points.append((x, y))
    
    # Draw the updated graph
    canvas = np.ones((height, width, 3), dtype=np.uint8) * 255  # Clear canvas
    
    # Draw axes
    cv2.line(canvas, (50, height - 50), (width - 50, height - 50), (0, 0, 0), 2)  # X-axis
    cv2.line(canvas, (50, height - 50), (50, 50), (0, 0, 0), 2)  # Y-axis

    # Plot points
    # for i in range(1, len(points)):
    #     cv2.line(canvas, points[i - 1], points[i], (255, 0, 0), 2)
    #     cv2.circle(canvas, points[i], 3, (0, 0, 255), -1)

    # Show the updated image
    cv2.imshow("Real-Time Graph", canvas)
    
    # Break if 'q' is pressed
    if cv2.waitKey(500) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
