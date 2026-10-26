# main.py

import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from generate_window import GenerateWindow
from read_screen import ScreenReader
from action_handler import ActionHandler

# Configuration file name
CONFIG_FILE = "coords_config.json"

# Default coordinates (fallback if configuration file is absent)
DEFAULT_AREAS = {
    "multiplier": {"top": 419, "left": 759, "width": 344, "height": 109},
    "balance": {"top": 222, "left": 1271, "width": 115, "height": 57},
    "history": {"top": 263, "left": 417, "width": 956, "height": 57},
    "bet_amount": {"top": 686, "left": 480, "width": 150, "height": 57},
    "bet_button": {"top": 712, "left": 634, "width": 218, "height": 67}
}


class MainController(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bot Controller")
        self.setGeometry(50, 50, 250, 250)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # Load coordinates from config or defaults
        self.current_areas = self.load_config()

        self.generated_windows = []
        self.setMinimumSize(1, 1)

        self.reader = ScreenReader()
        self.action = ActionHandler()

        # Bot strategy variables
        self.current_bet = 1.0
        self.target_multiplier = 2.5
        self.is_betting_cycle = False
        self.bet_placed_this_round = False
        self.last_processed_crash = None

        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.scan_screen)

        # Layout setup
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.btn_gen = QPushButton("🎯 1. Set Coordinates")
        self.btn_gen.setStyleSheet("padding: 10px; background-color: #007bff; color: white; font-weight: bold;")
        self.btn_gen.clicked.connect(self.generate_windows)

        self.btn_get = QPushButton("📥 2. Get Coordinates")
        self.btn_get.setStyleSheet("padding: 10px; background-color: #28a745; color: white; font-weight: bold;")
        self.btn_get.clicked.connect(self.collect_and_save)
        self.btn_get.setDisabled(True)

        self.btn_scan = QPushButton("▶️ 3. Start Scanning")
        self.btn_scan.setStyleSheet("padding: 10px; background-color: #17a2b8; color: white; font-weight: bold;")
        self.btn_scan.clicked.connect(self.toggle_scanning)
        self.btn_scan.setDisabled(True)

        layout.addWidget(self.btn_gen)
        layout.addWidget(self.btn_get)
        layout.addWidget(self.btn_scan)
        self.setLayout(layout)

    def load_config(self):
        """Loads coordinates from file, or returns default areas if unavailable."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    print("📂 Config loaded from file.")
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error reading config file: {e}")
                return DEFAULT_AREAS.copy()
        return DEFAULT_AREAS.copy()

    def save_config(self, data):
        """Persists coordinate dictionary to JSON file."""
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)
                print("💾 Coordinates saved to coords_config.json!")
        except Exception as e:
            print(f"⚠️ Error saving config: {e}")

    def generate_windows(self):
        """Generates draggable overlay windows for visual coordinate calibration."""
        self.generated_windows.clear()
        for name, coords in self.current_areas.items():
            win = GenerateWindow(
                title=name,
                x=coords["left"],
                y=coords["top"],
                w=coords["width"],
                h=coords["height"]
            )
            self.generated_windows.append(win)
        self.btn_gen.setDisabled(True)
        self.btn_get.setDisabled(False)

    def collect_and_save(self):
        """Extracts new positions from overlay windows, saves them, and closes overlays."""
        new_coords = {}
        for win in self.generated_windows:
            title, coords = win.get_location_dict()
            new_coords[title] = coords
            win.close_window()

        self.current_areas = new_coords
        self.save_config(new_coords)

        self.generated_windows.clear()
        self.btn_gen.setDisabled(False)
        self.btn_get.setDisabled(True)
        self.btn_scan.setDisabled(False)
        print("\n✅ New coordinates applied and saved!")

    def toggle_scanning(self):
        """Starts or stops the screen scanning timer loop."""
        if self.scan_timer.isActive():
            self.scan_timer.stop()
            self.btn_scan.setText("▶️ Start Scanning")
            print("🛑 Scanning stopped.")
        else:
            self.scan_timer.start(1000)
            self.btn_scan.setText("⏹️ Stop Scanning")
            print("🚀 Scanning started...")

    def scan_screen(self):
        """Scans defined screen areas, parses game state, and executes automated actions."""
        res = self.reader.get_text_from_areas(self.current_areas)
        multi_text = str(res.get('multiplier', '')).strip()
        hist_data = res.get('history', [])

        # Parse history numbers safely
        history = []
        if isinstance(hist_data, list):
            for x in hist_data:
                try:
                    history.append(float(x))
                except (ValueError, TypeError):
                    pass
        else:
            clean_str = str(hist_data).replace('[', '').replace(']', '').split(',')
            for x in clean_str:
                try:
                    history.append(float(x.strip()))
                except (ValueError, TypeError):
                    pass

        if not history:
            return

        current_last_crash = history[0]

        # Round interval / Countdown detected (multiplier text is blank)
        if multi_text == "":
            # Prevent duplicate processing of the same round
            if self.last_processed_crash == current_last_crash:
                return

            if not self.bet_placed_this_round and len(history) >= 2:
                # 1. Update cycle state based on last round result
                if self.is_betting_cycle:
                    if current_last_crash < self.target_multiplier:
                        self.current_bet *= 2
                        print(f"❌ Loss! Next Bet: {self.current_bet}")
                    else:
                        self.current_bet = 1.0
                        self.is_betting_cycle = False
                        print("✅ WIN! Resetting cycle.")

                # 2. Check trigger entry condition (e.g. 4 consecutive values below 2.0)
                if not self.is_betting_cycle:
                    if len(history) >= 4 and all(x < 2.0 for x in history[:4]):
                        self.is_betting_cycle = True
                        self.current_bet = 1.0
                        print(f"🎯 Entry condition met! Starting cycle with bet: {self.current_bet}")
                    else:
                        self.last_processed_crash = current_last_crash
                        return

                # 3. Place bet if in active cycle
                if self.is_betting_cycle:
                    print(f"🎰 Placing bet: {self.current_bet}")
                    self.action.place_bet(self.current_areas, self.current_bet)

                self.bet_placed_this_round = True
                self.last_processed_crash = current_last_crash
        else:
            # Game round is currently in progress
            self.bet_placed_this_round = False

    def closeEvent(self, event):
        """Cleanup resources on application close."""
        self.reader.close_reader()
        event.accept()


def main():
    app = QApplication(sys.argv)
    controller = MainController()
    controller.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()