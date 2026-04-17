import time
import sys
import cv2
import numpy as np
import pandas as pd
import mss
import easyocr
from tools.vehicle_box_filter import vehicle_box_filter
from tools.processing import find_index, remove_leading_numbers

DEBUG = '--debug' in sys.argv
reader = easyocr.Reader(['en'])


def show_interaction_window(vehicle_count):
    window_width, window_height = 600, 250
    cv2.namedWindow('Vehicle Logger', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Vehicle Logger', window_width, window_height)
    status_img = np.zeros((window_height, window_width, 3), dtype=np.uint8)

    # Displaying vehicle count
    cv2.putText(status_img, f"Vehicles Detected: {vehicle_count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Display instructions
    cv2.putText(status_img, "Instructions: Slowly scroll through your GV car list. " \
                            "When all cars have been scanned, press g.", (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    cv2.putText(status_img, "The excel sheet will be placed in the current directory.", (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    cv2.putText(status_img, "Press 'q' to quit", (20, 170),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
    cv2.putText(status_img, "Press 'g' to generate the excel spreadsheet.", (20, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
    
    cv2.imshow("Vehicle Logger", status_img)


def main():
    with mss.mss() as sct:
        monitor = sct.monitors[1] # Capturing the primary monitor

        # Showing the initial interaction window
        show_interaction_window(0)
        
        # The final deduplicated list of vehicles
        vehicle_dict = {}

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
                result = reader.readtext(roi, detail=0)
                roi_results.append(result)
            
            # Processing the regions of interest into a dictionary structure
            for roi_result in roi_results:
                # Getting teh make/model and trim
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
                if not odometer:
                    odometer = "0.0 miles"

                if " miles" not in odometer:
                    odometer = odometer.replace("miles", " miles")

                rims = roi_result[rims_index:] if rims_index != -1 else None
                rims_string = " ".join(rims).replace("Rims:", "").strip()                

                # Getting the color based on the odometer and rim indexes
                color = roi_result[odometer_index+1:rims_index] if odometer_index != -1 and rims_index != -1 else None
                color_string = " ".join(color).replace("miles", "").strip()

                # Cleaning the color string for Odometer abnormalities
                color_string = color_string.replace("miles", "").strip()
                color_string = remove_leading_numbers(color_string)
                color_string = color_string.replace("O ", "").strip() if color_string.startswith("O ") else color_string

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

                    vehicle_dict[(make_model, trim)] = vehicle_info


                show_interaction_window(len(vehicle_dict))

            # Debugging mode to show the detected ROIs
            if DEBUG:
                for i, roi in enumerate(rois):
                    cv2.namedWindow(f'ROI {i}', cv2.WINDOW_NORMAL)
                    cv2.moveWindow(f'ROI {i}', -900, i * 200)
                    cv2.imshow(f'ROI {i}', roi)

            # Detecting any 'q' presses
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            elif cv2.waitKey(1) & 0xFF == ord('g'):
                # Saving the vehicle information to an excel sheet
                df = pd.DataFrame(vehicle_dict.values())
                df.to_excel("vehicle_log.xlsx", index=False)
                print("Excel sheet generated: vehicle_log.xlsx")
            time.sleep(0.1)

        # Destroying any OpenCV windows during shutdown
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
