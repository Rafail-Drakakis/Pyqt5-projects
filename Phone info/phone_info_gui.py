import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QFileDialog, QMessageBox, QTabWidget,
                             QGroupBox, QProgressBar, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from phonenumbers import parse, is_valid_number, timezone, carrier, geocoder
import phonenumbers

class PhoneInfoWorker(QThread):
    """Worker thread for processing phone numbers to keep UI responsive"""
    progress_updated = pyqtSignal(int)
    info_ready = pyqtSignal(str)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, phone_numbers, filename):
        super().__init__()
        self.phone_numbers = phone_numbers if isinstance(phone_numbers, list) else [phone_numbers]
        self.filename = filename
        self.is_running = True
    
    def run(self):
        try:
            total = len(self.phone_numbers)
            results = []
            
            for i, phone_number in enumerate(self.phone_numbers):
                if not self.is_running:
                    break
                    
                info = self.get_phone_info(phone_number.strip())
                results.append(info)
                
                progress = int((i + 1) / total * 100)
                self.progress_updated.emit(progress)
            
            if self.is_running:
                # Save to file
                with open(self.filename, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(results))
                
                self.info_ready.emit('\n'.join(results))
            
        except Exception as e:
            self.error_occurred.emit(f"Error processing phone numbers: {str(e)}")
        finally:
            self.finished.emit()
    
    def get_phone_info(self, mobile_number):
        """Extract phone number information"""
        try:
            parsed_number = parse(mobile_number)
            if is_valid_number(parsed_number):
                info_lines = []
                info_lines.append(f"Phone Number: {parsed_number}")
                
                # Time zones
                time_zones = timezone.time_zones_for_number(parsed_number)
                if time_zones:
                    info_lines.append(f"Region/Timezone: {', '.join(time_zones)}")
                else:
                    info_lines.append("Region/Timezone: Not found")
                
                # Carrier
                carrier_name = carrier.name_for_number(parsed_number, "en")
                info_lines.append(f"Service Provider: {carrier_name if carrier_name else 'Unknown'}")
                
                # Country
                country = geocoder.description_for_number(parsed_number, "en")
                info_lines.append(f"Country: {country if country else 'Unknown'}")
                
                # Number type
                number_type = phonenumbers.number_type(parsed_number)
                type_names = {
                    phonenumbers.PhoneNumberType.MOBILE: "Mobile",
                    phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
                    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
                    phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
                    phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
                    phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
                    phonenumbers.PhoneNumberType.VOIP: "VoIP",
                    phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
                    phonenumbers.PhoneNumberType.PAGER: "Pager",
                    phonenumbers.PhoneNumberType.UAN: "UAN",
                    phonenumbers.PhoneNumberType.UNKNOWN: "Unknown"
                }
                info_lines.append(f"Number Type: {type_names.get(number_type, 'Unknown')}")
                
                info_lines.append("-" * 50)
                return '\n'.join(info_lines)
            else:
                return f"Invalid phone number: {mobile_number}\n" + "-" * 50
        except Exception as e:
            return f"Error processing {mobile_number}: {str(e)}\n" + "-" * 50
    
    def stop(self):
        self.is_running = False

class PhoneNumberInfoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        self.setWindowTitle("Phone Number Information Analyzer")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Phone Number Information Analyzer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 20px;")
        main_layout.addWidget(title_label)
        
        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_single_number_tab(), "Single Number")
        tab_widget.addTab(self.create_bulk_processing_tab(), "Bulk Processing")
        main_layout.addWidget(tab_widget)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("background-color: #34495e; color: white; padding: 5px;")
    
    def create_single_number_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input group
        input_group = QGroupBox("Phone Number Input")
        input_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        input_layout = QVBoxLayout(input_group)
        
        # Phone number input
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("Phone Number:"))
        self.single_phone_input = QLineEdit()
        self.single_phone_input.setPlaceholderText("Enter phone number with country code (e.g., +1234567890)")
        self.single_phone_input.returnPressed.connect(self.analyze_single_number)
        phone_layout.addWidget(self.single_phone_input)
        input_layout.addLayout(phone_layout)
        
        # Filename input
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Output File:"))
        self.single_filename_input = QLineEdit()
        self.single_filename_input.setPlaceholderText("Enter filename to save results (e.g., phone_info.txt)")
        self.single_filename_input.setText("phone_info.txt")
        file_layout.addWidget(self.single_filename_input)
        
        self.single_browse_btn = QPushButton("Browse")
        self.single_browse_btn.clicked.connect(self.browse_save_file)
        file_layout.addWidget(self.single_browse_btn)
        input_layout.addLayout(file_layout)
        
        # Analyze button
        self.single_analyze_btn = QPushButton("Analyze Phone Number")
        self.single_analyze_btn.clicked.connect(self.analyze_single_number)
        self.single_analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        input_layout.addWidget(self.single_analyze_btn)
        
        layout.addWidget(input_group)
        
        # Results area
        results_group = QGroupBox("Analysis Results")
        results_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        results_layout = QVBoxLayout(results_group)
        
        self.single_results = QTextEdit()
        self.single_results.setReadOnly(True)
        self.single_results.setPlaceholderText("Analysis results will appear here...")
        results_layout.addWidget(self.single_results)
        
        layout.addWidget(results_group)
        
        return tab
    
    def create_bulk_processing_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input group
        input_group = QGroupBox("Bulk Processing")
        input_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        input_layout = QVBoxLayout(input_group)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Input File:"))
        self.bulk_file_input = QLineEdit()
        self.bulk_file_input.setPlaceholderText("Select a text file containing phone numbers (one per line)")
        self.bulk_file_input.setReadOnly(True)
        file_layout.addWidget(self.bulk_file_input)
        
        self.bulk_browse_btn = QPushButton("Browse")
        self.bulk_browse_btn.clicked.connect(self.browse_input_file)
        file_layout.addWidget(self.bulk_browse_btn)
        input_layout.addLayout(file_layout)
        
        # Output filename
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output File:"))
        self.bulk_filename_input = QLineEdit()
        self.bulk_filename_input.setPlaceholderText("Enter filename to save results")
        self.bulk_filename_input.setText("phone_info.txt")
        output_layout.addWidget(self.bulk_filename_input)
        
        self.bulk_save_browse_btn = QPushButton("Browse")
        self.bulk_save_browse_btn.clicked.connect(self.browse_save_file_bulk)
        output_layout.addWidget(self.bulk_save_browse_btn)
        input_layout.addLayout(output_layout)
        
        # Process button
        self.bulk_process_btn = QPushButton("Process Phone Numbers")
        self.bulk_process_btn.clicked.connect(self.process_bulk_numbers)
        self.bulk_process_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        input_layout.addWidget(self.bulk_process_btn)
        
        layout.addWidget(input_group)
        
        # Results area
        results_group = QGroupBox("Processing Results")
        results_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        results_layout = QVBoxLayout(results_group)
        
        self.bulk_results = QTextEdit()
        self.bulk_results.setReadOnly(True)
        self.bulk_results.setPlaceholderText("Bulk processing results will appear here...")
        results_layout.addWidget(self.bulk_results)
        
        layout.addWidget(results_group)
        
        return tab
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-family: 'Courier New', monospace;
                line-height: 1.4;
            }
            QGroupBox {
                font-size: 14px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
    
    def browse_save_file(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Results As", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            self.single_filename_input.setText(filename)
    
    def browse_save_file_bulk(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Results As", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            self.bulk_filename_input.setText(filename)
    
    def browse_input_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Phone Numbers File", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            self.bulk_file_input.setText(filename)
    
    def analyze_single_number(self):
        phone_number = self.single_phone_input.text().strip()
        filename = self.single_filename_input.text().strip()
        
        if not phone_number:
            QMessageBox.warning(self, "Warning", "Please enter a phone number.")
            return
        
        if not filename:
            QMessageBox.warning(self, "Warning", "Please enter a filename.")
            return
        
        self.start_processing([phone_number], filename, self.single_results)
    
    def process_bulk_numbers(self):
        input_file = self.bulk_file_input.text().strip()
        output_file = self.bulk_filename_input.text().strip()
        
        if not input_file:
            QMessageBox.warning(self, "Warning", "Please select an input file.")
            return
        
        if not output_file:
            QMessageBox.warning(self, "Warning", "Please enter an output filename.")
            return
        
        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                phone_numbers = [line.strip() for line in file.readlines() if line.strip()]
            
            if not phone_numbers:
                QMessageBox.warning(self, "Warning", "The input file is empty or contains no valid phone numbers.")
                return
            
            self.start_processing(phone_numbers, output_file, self.bulk_results)
            
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "Input file not found. Please check the file path.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading input file: {str(e)}")
    
    def start_processing(self, phone_numbers, filename, results_widget):
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "Info", "Processing is already in progress.")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.single_analyze_btn.setEnabled(False)
        self.bulk_process_btn.setEnabled(False)
        
        self.statusBar().showMessage("Processing phone numbers...")
        results_widget.clear()
        results_widget.append("Processing started...\n")
        
        self.worker = PhoneInfoWorker(phone_numbers, filename)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.info_ready.connect(lambda info: self.on_processing_finished(info, results_widget, filename))
        self.worker.error_occurred.connect(self.on_error)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()
    
    def on_processing_finished(self, info, results_widget, filename):
        results_widget.clear()
        results_widget.append(info)
        QMessageBox.information(
            self, "Success", 
            f"Phone number analysis completed successfully!\nResults saved to: {filename}"
        )
        self.statusBar().showMessage(f"Analysis completed. Results saved to {filename}")
    
    def on_error(self, error_msg):
        QMessageBox.critical(self, "Error", error_msg)
        self.statusBar().showMessage("Error occurred during processing")
    
    def on_worker_finished(self):
        self.progress_bar.setVisible(False)
        self.single_analyze_btn.setEnabled(True)
        self.bulk_process_btn.setEnabled(True)
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "Confirm Exit",
                "Processing is still in progress. Do you want to stop and exit?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Set application properties
    app.setApplicationName("Phone Number Info Analyzer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("PhoneAnalyzer")
    
    window = PhoneNumberInfoGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()