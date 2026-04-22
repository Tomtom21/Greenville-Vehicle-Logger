import time
import sys
import cv2
import numpy as np
import pandas as pd
import mss
import imagehash
import os
from tools.vehicle_box_filter import vehicle_box_filter
from tools.processing import find_index, remove_leading_numbers
from PIL import Image

DEBUG = '--debug' in sys.argv
SAVE_FOLDER = 'images'
THRESHOLD = 6

def show_interaction_window():
    window_width, window_height = 600, 250
    cv2.namedWindow('Vehicle Logger', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Vehicle Logger', window_width, window_height)
    status_img = np.zeros((window_height, window_width, 3), dtype=np.uint8)

    # display placeholder
    cv2.putText(status_img, 'Placeholder', (10, 50),
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    
    cv2.imshow("Vehicle Logger", status_img)

def is_similar(new_hash, existing_hash):
    for h in existing_hash:
        if new_hash - h <= THRESHOLD:
            return True
    return False

def compute_hash(roi):
    # normalize image
    roi = cv2.resize(roi, (128, 128))
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi = cv2.GaussianBlur(roi, (5, 5), 0)

    pil_img = Image.fromarray(roi)

    # combine hashes for better accuracy
    ph = imagehash.phash(pil_img)
    dh = imagehash.dhash(pil_img)

    combined = ph.hash ^ dh.hash
    return imagehash.ImageHash(combined)

def main():
    # create image folder if it does not exist
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    existing_hashes = [] # store hashes of saved images
    img_counter = 0

    with mss.mss() as sct:
        monitor = sct.monitors[1] # Capturing the primary monitor

        # Showing the initial interaction window
        show_interaction_window()

        while True:
            # Getting an image (ignoring any alpha channel)
            sct_img = sct.grab(monitor)
            frame = np.array(sct_img)
            if frame.shape[2] == 4:
                frame = frame[:, :, :3]

            # Getting ROIs for vehicles
            rois = vehicle_box_filter(frame, 
                                      lower_color=np.array([64, 64, 64]), 
                                      upper_color=np.array([66, 66, 66]),
                                      min_size=(200, 210))

            # hash and deduplicate images
            for i, roi in enumerate(rois):
                try:
                    # grab image
                    height, width = roi.shape[:2]

                    # crop image
                    roi_cropped = roi[int(height * 0.125):int(height * 0.9),
                                  int(width * 0.35):int(width * 0.7)]

                    # compute hash
                    hash = compute_hash(roi_cropped)

                    # check similarity
                    if not is_similar(hash, existing_hashes):
                        filename = f'{SAVE_FOLDER}/roi_{int(time.time())}_{img_counter}.jpg'
                        cv2.imwrite(filename, roi_cropped)

                        existing_hashes.append(hash)
                        print(f'Saved (new): {filename}')
                        img_counter += 1
                    else:
                        print(f'Skipped similar image')

                except Exception as e:
                    print(f'Error processing ROI: {e}')

            # Debugging mode to show the detected ROIs
            if DEBUG:
                for i, roi in enumerate(rois):
                    cv2.namedWindow(f'ROI {i}', cv2.WINDOW_NORMAL)
                    #cv2.moveWindow(f'ROI {i}', -900, i * 200)
                    cv2.moveWindow(f'ROI {i}', 5120, (i * 200) + 600)
                    cv2.imshow(f'ROI {i}', roi)
                    cv2.resizeWindow(f'ROI {i}', roi.shape[1], roi.shape[0])

            # Detecting any 'q' presses
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.1)

        # Destroying any OpenCV windows during shutdown
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
