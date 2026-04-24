import re

def find_index(roi_result, keyword):
    for idx, text in enumerate(roi_result):
        if keyword in text:
            return idx
    return -1

def remove_leading_numbers(s):
    return re.sub(r'^\d+', '', s).strip()
