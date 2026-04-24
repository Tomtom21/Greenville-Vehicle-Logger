import cv2
import numpy as np

class InteractionMenu:
    def __init__(self):
        self.window_width = 600
        self.window_height = 250

    def get_basic_background_img(self):
        # Background image
        img = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)
        return img
    
    def draw_start_page(self):
        img = self.get_basic_background_img()

        # Saying hi and giving instructions
        cv2.putText(img,
                    "Instructions: Slowly scroll through your GV car list. " \
                    "When all cars have been scanned, press g.", 
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    (255, 255, 255),
                    1)
        cv2.putText(img,
                    "The excel sheet will be placed in the current directory.", 
                    (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    (255, 255, 255),
                    1)
        
        # Button instructions
        cv2.putText(img, "Press 'q' to quit", (20, 170),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(img, "Press any key to continue", (20, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
        return img
    
    def draw_count_page(self, vehicle_count):
        img = self.get_basic_background_img()

        # Displaying vehicle count
        cv2.putText(img, 
                    f"Vehicles Detected: {vehicle_count}", 
                    (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.8, 
                    (255, 255, 255), 
                    2)
        
        # Button instructions
        cv2.putText(img, "Press 'q' to quit", (20, 170),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
        cv2.putText(img, "Press 'g' to generate the excel spreadsheet.", (20, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
        return img
    
    def wait_for_commands(self, on_quit_func, on_quit_key, on_generate_func, on_generate_key, wait_time=1):
        key = cv2.waitKey(wait_time) & 0xFF
        if key == ord(on_quit_key):
            on_quit_func()
        elif key == ord(on_generate_key):
            on_generate_func()
    
