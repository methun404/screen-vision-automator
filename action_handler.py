# action_handler.py

import pyautogui
import time


class ActionHandler:
    def __init__(self):
        # Set low pause interval (0.05s) for responsive automation
        pyautogui.PAUSE = 0.05

    def get_center(self, coords):
        """Calculates center coordinate (x, y) from bounding box dict."""
        center_x = coords["left"] + (coords["width"] / 2)
        center_y = coords["top"] + (coords["height"] / 2)
        return center_x, center_y

    def place_bet(self, areas_dict, amount):
        amount_box = areas_dict.get("bet_amount")
        box_x, box_y = self.get_center(amount_box)

        # 1. Triple-click to select all text within input field
        pyautogui.click(box_x, box_y, clicks=3, interval=0.02)
        time.sleep(0.05)  # Small delay for UI focus/selection

        # 2. Clear selected text rapidly (with backspace fallback)
        pyautogui.press('backspace', presses=10, interval=0.01)

        # 3. Type new amount instantly
        pyautogui.write(str(amount))

        # 4. Click the confirmation/action button
        bet_btn = areas_dict.get("bet_button")
        btn_x, btn_y = self.get_center(bet_btn)
        pyautogui.click(btn_x, btn_y)

        print(f"✅ Bet placed: {amount}")