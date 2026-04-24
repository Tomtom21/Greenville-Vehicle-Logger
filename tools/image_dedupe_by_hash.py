"""
For the initial de-duplication of images during image capture
"""

import imagehash
from PIL import Image

class ImageDedupeByHash:
    def __init__(self):
        # Our dictionary to store the hash values and their corresponding image
        self.hash_dict = {}

    def calc_hash(self, img):
        """
        Calculating the hash of an image
        :param img: The image to calculate the hash for (PIL Image)
        :return: The hash of the image
        """
        # Converting the image to PIL
        pil_img = Image.fromarray(img)

        # Compute the hash of the image
        return imagehash.dhash(pil_img)

    def add_image(self, img):
        # Compute the hash of the image
        img_hash = self.calc_hash(img)

        # Checking if any existing hash is within a certain hamming distance (e.g., 8) of the new hash
        is_duplicate = any((img_hash - existing_hash) <= 4 for existing_hash in self.hash_dict.keys())

        if not is_duplicate:
            self.hash_dict[img_hash] = img

    def __len__(self):
        return len(self.hash_dict)
