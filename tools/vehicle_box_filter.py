import numpy as np
import cv2

def vehicle_box_filter(img, lower_color: np.ndarray, upper_color: np.ndarray, min_size=(20, 20)):
    """
    Generates bounding boxes for an image based off of objects within a known color range.

    :param img: The image to process (BGR format)
    :param lower_color: The lower bound of the color range (BGR format)
    :param upper_color: The upper bound of the color range (BGR format)
    :param min_size: The minimum size of the bounding boxes (width, height)
    """

    # Making sure our color ranges are valid (np.ndarray of shape (3,))
    if not (isinstance(lower_color, np.ndarray) and lower_color.shape == (3,)):
        raise ValueError("lower_color must be a numpy ndarray of shape (3,)")
    if not (isinstance(upper_color, np.ndarray) and upper_color.shape == (3,)):
        raise ValueError("upper_color must be a numpy ndarray of shape (3,)")

    # Generating a mask and using contours to find bounding boxes for objects
    mask = cv2.inRange(img, lower_color, upper_color)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions_of_interest = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > min_size[0] and h > min_size[1]: # Filtering out small boxes
            regions_of_interest.append(img[y:y+h, x:x+w])

    return regions_of_interest
