import time
import sys
import cv2
import numpy as np
import mss
import easyocr
from tools.vehicle_box_filter import vehicle_box_filter

DEBUG = '--debug' in sys.argv
reader = easyocr.Reader(['en'])

def find_index(roi_result, keyword):
    for idx, text in enumerate(roi_result):
        if keyword in text:
            return idx
    return -1

def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    return enhanced

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
            rois = vehicle_box_filter(frame, 
                                      lower_color=np.array([64, 64, 64]), 
                                      upper_color=np.array([66, 66, 66]),
                                      min_size=(200, 150))

            # Reading the regions of interest with EasyOCR
            roi_results = []
            for roi in rois:
                # Using EasyOCR to read text from the ROI
                preprocessed_image = preprocess_image(roi)
                result = reader.readtext(preprocessed_image, detail=0)
                roi_results.append(result)
            
            # Processing the regions of interest into a dictionary structure
            for roi_result in roi_results:
                make_model = roi_result[0] if len(roi_result) > 0 else None
                trim = roi_result[1] if "(" in  roi_result[1] and ")" in roi_result[1] else None

                # Determining the index of the Odometer and Rims
                odometer_index = find_index(roi_result, "Odometer:")
                rims_index = find_index(roi_result, "Rims:")

                # Collecting tags for the vehicles
                tags = roi_result[1+1:odometer_index] if odometer_index != -1 else []
                tags_string = ", ".join(tags)

                # Collecting the rest of the vehicle information
                odometer = roi_result[odometer_index].replace("Odometer:", "").strip() if odometer_index != -1 else None
                rims = roi_result[rims_index:] if rims_index != -1 else None
                rims_string = " ".join(rims).replace("Rims:", "").strip()


                # Might have to manually tell it to remove miles from the start of color
                # If the odometer is missing, we can assume that there are probably 0 miles on the car
                

                # Getting the color based on the odometer and rim indexes
                color = roi_result[odometer_index+1:rims_index] if odometer_index != -1 and rims_index != -1 else None
                color_string = " ".join(color)

                # Making sure we got all of the information
                if None not in (make_model, trim, odometer, rims):
                    vehicle_info = {
                        "Make and Model": make_model,
                        "Trim": trim,
                        "Tags": tags_string,
                        "Odometer": odometer,
                        "Color": color_string,
                        "Rims": rims_string
                    }
                    print(vehicle_info)
                    print("")
                

            # Debugging mode to show the detected ROIs
            if DEBUG:
                for i, roi in enumerate(rois):
                    preprocessed_image = preprocess_image(roi)
                    cv2.namedWindow(f'ROI {i}', cv2.WINDOW_NORMAL)
                    cv2.moveWindow(f'ROI {i}', -900, i * 200)
                    cv2.imshow(f'ROI {i}', preprocessed_image)

            # Detecting any 'q' presses
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.3)

        # Destroying any OpenCV windows during shutdown
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
