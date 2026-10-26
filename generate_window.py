# generate_window.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class GenerateWindow:
    def __init__(self, title, x, y, w, h):
        self.title = title
        self.window = QWidget()

        # 1. Allow window to be scaled down to 1 pixel minimum
        self.window.setMinimumSize(1, 1)

        self.window.setWindowTitle(title)
        self.window.setGeometry(x, y, w, h)
        self.window.setWindowOpacity(0.6)
        self.window.setStyleSheet("background-color: #007bff;")  # Blue accent color

        # Keep overlay window floating on top of all other windows
        self.window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        # Layout and label to display the area title in the center of the window
        layout = QVBoxLayout()

        # 2. Reset layout margins and spacing to zero
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label = QLabel(self.title.upper())
        label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 3. Prevent label dimensions from constraining window resizing
        label.setMinimumSize(0, 0)

        layout.addWidget(label)

        self.window.setLayout(layout)
        self.window.show()

    def get_location_dict(self):
        """Returns the updated overlay coordinates as a dictionary."""
        x = self.window.geometry().x()
        y = self.window.geometry().y()
        w = self.window.geometry().width()
        h = self.window.geometry().height()
        return self.title, {"top": y, "left": x, "width": w, "height": h}

    def close_window(self):
        """Closes and hides the overlay window."""
        self.window.close()


# Backward compatibility alias
GenarateWindow = GenerateWindow
