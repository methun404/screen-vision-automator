# read_screen.py

import re
import mss
import numpy as np
import cv2
import pytesseract


class ScreenReader:
    def __init__(self):
        # Initialize mss screen capture instance once to minimize overhead
        self.sct = mss.mss()
        # Configure Tesseract OCR for single-line numbers and decimal values
        self.tess_config = '--psm 7 -c tessedit_char_whitelist=0123456789.x'

    def get_text_from_areas(self, areas_dict):
        extracted_result = {
            "multiplier": 0,
            "balance": 0,
            "history": [],
            "bet_amount": 0,
        }

        # Iterate through target coordinate areas
        for area, coords in areas_dict.items():
            if area == "bet_button":
                continue

            # Capture screen region and convert to grayscale
            screenshot = self.sct.grab(coords)
            img = np.array(screenshot)
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

            # Extract text via OCR
            extracted_text = pytesseract.image_to_string(gray, config=self.tess_config)
            clean_text = extracted_text.strip()

            # Parse extracted data according to region type
            if area == "history":
                numbers = re.findall(r'\d+\.\d+', clean_text)
                numbers = [float(n) for n in numbers]
                # Exclude trailing element if present
                extracted_result["history"] = numbers[:-1] if numbers else []

            elif area == "bet_amount":
                extracted_result["bet_amount"] = clean_text

            elif area == "balance":
                extracted_result["balance"] = clean_text

            elif area == "multiplier":
                extracted_result["multiplier"] = clean_text.replace('x', '').replace('X', '').strip()

        return extracted_result

    def close_reader(self):
        """Close mss capture instance cleanly."""
        self.sct.close()