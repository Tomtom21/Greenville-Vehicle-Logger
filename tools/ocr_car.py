"""
Defining the class that holds the individual OCR-detected results for cars.
"""

from tools.processing import find_index, remove_leading_numbers

class OCRCar:
    def __init__(self, ocr_reader, image):
        self.make_model = None
        self.trim = None
        self.odometer = None
        self.rims = None
        self.tags = []
        self.color_string = None

        # Getting the ocr result
        result_text = ocr_reader.readtext(image, detail=0)

        # Getting indexes of the odometer and rims first
        odometer_index = find_index(result_text, "Odometer:")
        rims_index = find_index(result_text, "Rims:")

        # Parsing the make/model and trim
        if len(result_text) > 0:
            self.make_model = result_text[0]

        if len(result_text) > 1 and "(" in result_text[1] and ")" in result_text[1]:
            self.trim = result_text[1]

        # Parsing the tags, odometer
        if odometer_index < len(result_text) and odometer_index != -1:
            tags_list = result_text[1+1:odometer_index]
            self.tags = ", ".join(tags_list)

            self.odometer = result_text[odometer_index].replace("Odometer:", "").strip()
            if not self.odometer:
                self.odometer = "0.0 miles"
            
            if " miles" not in self.odometer:
                self.odometer = self.odometer.replace("miles", " miles")

        # Parsing the color and rims
        if rims_index < len(result_text) and rims_index != -1:
            rims_list = result_text[rims_index:]
            self.rims = " ".join(rims_list).replace("Rims:", "").strip()
            
            color_list = result_text[odometer_index+1:rims_index]
            self.color_string = " ".join(color_list).replace("miles", "").strip()
            
            # Cleaning the color string
            self.color_string = self.color_string.replace("miles", "").strip()
            self.color_string = remove_leading_numbers(self.color_string)
            if self.color_string.startswith("O "):
                self.color_string = self.color_string.replace("O ", "").strip()

    def get_dict(self):
        vehicle_info = {
            "Make and Model": self.make_model,
            "Trim": self.trim,
            "Tags": self.tags,
            "Odometer": self.odometer,
            "Color": self.color_string,
            "Rims": self.rims
        }
        return vehicle_info
