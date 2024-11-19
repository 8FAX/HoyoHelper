import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QCheckBox,
    QListWidget,
    QWidget,
)
from PyQt5.QtCore import Qt
import os


class ThemeTesterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Tester")

        # Load the CSS
        self.load_css()

        # Central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()

        items = []

        for i in range(10):
            items.append(f"Item {i}")

        # Add sample widgets
        self.label = QLabel("This is a QLabel")
        self.line_edit = QLineEdit("This is a QLineEdit")
        self.checkbox = QCheckBox("This is a QCheckBox")
        self.button = QPushButton("This is a QPushButton")
        self.list_widget = QListWidget()
        self.list_widget.addItems(items)

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.button)
        layout.addWidget(self.list_widget)

        # Set layout to the central widget
        central_widget.setLayout(layout)


    def load_css(self):
        css_file_path = os.path.join(os.path.dirname(__file__), 'test.css')
        if os.path.exists(css_file_path):
            with open(css_file_path, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            print('CSS file not found:', css_file_path)


def main():
    app = QApplication(sys.argv)
    window = ThemeTesterApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
