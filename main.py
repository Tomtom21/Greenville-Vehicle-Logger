import time
import sys
import cv2
import numpy as np
import pandas as pd
import mss
import easyocr
from PIL import Image
from tools.vehicle_box_filter import vehicle_box_filter
from tools.processing import find_index, remove_leading_numbers
from tools.image_dedupe_by_hash import ImageDedupeByHash
from tools.ocr_car import OCRCar
from tools.gui import InteractionMenu
from tqdm import tqdm

DEBUG = '--debug' in sys.argv
reader = easyocr.Reader(['en'])

def on_quit():
    cv2.destroyAllWindows()
    sys.exit(0)

def main():
    with mss.mss() as sct:
        monitor = sct.monitors[1] # Capturing the primary monitor

        # Initiating the interaction menu
        interaction_menu = InteractionMenu()

        # Showing the initial interaction window
        img = interaction_menu.draw_start_page()
        cv2.imshow("Vehicle Logger", img)
        
        # Waiting for the user to respond
        def no_op():
            pass
        interaction_menu.wait_for_commands(on_quit, 'q', no_op, 'g', wait_time=0)

        # Initializing our image de-duplication class
        image_dedupe = ImageDedupeByHash()

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

            # Capturing de-duplicated ROIs
            for roi in rois:
                image_dedupe.add_image(roi)

            # Drawing the interaction window with the current vehicle count
            img = interaction_menu.draw_count_page(len(image_dedupe))
            cv2.imshow("Vehicle Logger", img)

            def post_process():
                cv2.destroyAllWindows()

                # Running OCR on the de-duplicated images and building the final vehicle dictionary
                # Key is (make/model, trim) and value is the full vehicle object
                print("Running optical character recognition on detected vehicles...")
                vehicle_data = {}
                for car in tqdm(image_dedupe.hash_dict.values()):
                    ocr_car = OCRCar(reader, car)
                    if all([ocr_car.make_model, ocr_car.trim, ocr_car.odometer, ocr_car.rims, ocr_car.color_string]):
                        vehicle_data[(ocr_car.make_model, ocr_car.trim)] = ocr_car.get_dict()

                # Saving the vehicle information to an excel sheet
                df = pd.DataFrame(vehicle_data.values())
                df.to_excel("vehicle_log.xlsx", index=False)
                print("Excel sheet generated: vehicle_log.xlsx")
                print("You can view this sheet in Microsoft Excel or Google Sheets.")
                print("Closing in 10 seconds...")
                time.sleep(10)
                exit(0)

            interaction_menu.wait_for_commands(on_quit, 'q', post_process, 'g', wait_time=1)

            # Debugging mode to show the detected ROIs
            if DEBUG:
                for i, roi in enumerate(rois):
                    cv2.namedWindow(f'ROI {i}', cv2.WINDOW_NORMAL)
                    cv2.moveWindow(f'ROI {i}', -900, i * 200)
                    cv2.imshow(f'ROI {i}', roi)
                
            time.sleep(0.1)

if __name__ == "__main__":
    main()
