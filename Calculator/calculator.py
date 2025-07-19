import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLineEdit, QCheckBox,
    QGridLayout, QPushButton
)

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setFixedSize(300, 400)
        self._central_widget = QWidget(self)
        self.setCentralWidget(self._central_widget)

        # Display setup
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setFixedHeight(40)
        self.display.setStyleSheet("font-size: 18px; padding: 5px;")

        # Scientific toggle
        self.scientific_checkbox = QCheckBox("Scientific")
        self.scientific_checkbox.stateChanged.connect(self.toggle_scientific)

        # Layout composition
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.display)
        self.main_layout.addWidget(self.scientific_checkbox)

        # Buttons grid
        self.buttons_widget = QWidget()
        self.buttons_layout = QGridLayout()
        self.buttons_layout.setSpacing(5)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self._central_widget.setLayout(self.main_layout)

        self._create_buttons()
        self.toggle_scientific()  # initialize view

    def _create_buttons(self):
        # Normal calculator buttons including parentheses and backspace
        self.normal_buttons = {
            '7': (0, 0), '8': (0, 1), '9': (0, 2), '/': (0, 3),
            '4': (1, 0), '5': (1, 1), '6': (1, 2), '*': (1, 3),
            '1': (2, 0), '2': (2, 1), '3': (2, 2), '-': (2, 3),
            '0': (3, 0), '.': (3, 1), '=': (3, 2), '+': (3, 3),
            'C': (4, 0), '(': (4, 1), ')': (4, 2), '⌫': (4, 3)
        }
        # Scientific calculator buttons, shifted down
        self.scientific_buttons = {
            'sin': (5, 0), 'cos': (5, 1), 'tan': (5, 2), 'log': (5, 3),
            'ln': (6, 0), 'sqrt': (6, 1), '^': (6, 2)
        }

        # Create normal buttons
        for text, pos in self.normal_buttons.items():
            btn = QPushButton(text)
            btn.setFixedSize(60, 40)
            btn.clicked.connect(lambda _, t=text: self.on_button_clicked(t))
            self.buttons_layout.addWidget(btn, pos[0], pos[1])

        # Create scientific buttons
        self.scientific_btn_refs = []
        for text, pos in self.scientific_buttons.items():
            btn = QPushButton(text)
            btn.setFixedSize(60, 40)
            btn.clicked.connect(lambda _, t=text: self.on_button_clicked(t))
            self.scientific_btn_refs.append(btn)
            self.buttons_layout.addWidget(btn, pos[0], pos[1])

    def toggle_scientific(self):
        show = self.scientific_checkbox.isChecked()
        for btn in self.scientific_btn_refs:
            btn.setVisible(show)
        # adjust window height based on mode
        height = 480 if show else 380
        self.setFixedSize(300, height)

    def on_button_clicked(self, char):
        if char == 'C':
            self.display.clear()
        elif char == '⌫':
            current = self.display.text()
            self.display.setText(current[:-1])
        elif char == '=':
            self.calculate()
        else:
            # translate '^' to '**'
            if char == '^':
                char = '**'
            # 'ln' -> natural log, insert math.log
            if char == 'ln':
                self.display.insert('log(')
                return
            # functions: append with parentheses
            if char in ('sin', 'cos', 'tan', 'log', 'sqrt'):
                self.display.insert(f"{char}(")
                return
            # default: number/operator/paren
            self.display.insert(char)

    def calculate(self):
        expr = self.display.text()
        try:
            # Safe evaluation environment
            allowed_names = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
            allowed_names.update({'abs': abs})
            result = eval(expr, {"__builtins__": None}, allowed_names)
            self.display.setText(str(result))
        except Exception:
            self.display.setText("Error")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
