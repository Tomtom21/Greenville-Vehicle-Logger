import time
import sys
import cv2
import numpy as np
import mss

from tools.vehicle_box_filter import vehicle_box_filter

DEBUG = '--debug' in sys.argv

def main():
    with mss.mss() as sct:
        monitor = sct.monitors[1] # Capturing the primary monitor

        while True:
            # Getting an image (ignoring any alpha channel)
            sct_img = sct.grab(monitor)
            frame = np.array(sct_img)
            if frame.shape[2] == 4:
                frame = frame[:, :, :3]

            # Getting ROIs for vehicles 
            rois = vehicle_box_filter(frame, lower_color=np.array([0, 0, 0]), upper_color=np.array([255, 255, 255]))

            # Debugging mode to show the detected ROIs
            if DEBUG:
                for i, roi in enumerate(rois):
                    cv2.imshow(f'ROI {i}', roi)

            # Detecting any 'q' presses
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.3)

        # Destroying any OpenCV windows during shutdown
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
