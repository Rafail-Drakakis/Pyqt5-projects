from PyQt5.QtWidgets import (
    QApplication, QWidget, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QVBoxLayout, QLabel
)
import sys

class CurrencyExchangeCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Currency Exchange Calculator")
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.initial_currency_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.target_currency_input = QLineEdit()
        self.exchange_rate_input = QLineEdit()
        self.new_exchange_rate_input = QLineEdit()

        form_layout.addRow("Initial Currency:", self.initial_currency_input)
        form_layout.addRow("Amount to Exchange:", self.amount_input)
        form_layout.addRow("Target Currency:", self.target_currency_input)
        form_layout.addRow("Exchange Rate (1 Initial = ? Target):", self.exchange_rate_input)
        form_layout.addRow("New Exchange Rate (1 Initial = ? Target):", self.new_exchange_rate_input)

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate_profit_loss)

        layout.addLayout(form_layout)
        layout.addWidget(self.calculate_button)

        self.setLayout(layout)

    def calculate_profit_loss(self):
        try:
            initial_currency = self.initial_currency_input.text().strip()
            amount = float(self.amount_input.text())
            exchange_rate = float(self.exchange_rate_input.text())
            new_exchange_rate = float(self.new_exchange_rate_input.text())

            target_amount = amount * exchange_rate
            new_amount = target_amount / new_exchange_rate
            profit_loss = new_amount - amount

            if profit_loss >= 0:
                result = f"Your profit would be {profit_loss:.2f} {initial_currency}."
            else:
                result = f"Your loss would be {-profit_loss:.2f} {initial_currency}."

            QMessageBox.information(self, "Result", result)
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numeric values.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CurrencyExchangeCalculator()
    window.show()
    sys.exit(app.exec_())

