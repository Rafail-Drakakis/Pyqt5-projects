import sys, json, os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QListWidget, QListWidgetItem, QLineEdit, QMessageBox, QLabel, QInputDialog,
    QComboBox, QColorDialog, QFrame, QSplitter
)
from PyQt5.QtGui import QTextCharFormat, QTextCursor, QFont, QPalette, QIcon
from PyQt5.QtCore import Qt

NOTES_FILE = "notes.json"
SETTINGS_FILE = "settings.json"

class SettingsManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding='utf-8') as f:
                    self.settings = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.settings = {"dark_theme": False}
        else:
            self.settings = {"dark_theme": False}

    def save_settings(self):
        try:
            with open(self.file_path, "w", encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

class NoteManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.notes = {}
        self.load_notes()

    def load_notes(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding='utf-8') as f:
                    self.notes = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.notes = {}
        else:
            self.notes = {}

    def save_notes(self):
        try:
            with open(self.file_path, "w", encoding='utf-8') as f:
                json.dump(self.notes, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving notes: {e}")

    def get_titles(self):
        return list(self.notes.keys())

    def get_note(self, title):
        return self.notes.get(title, {"content": "", "tags": []})

    def add_note(self, title, content="", tags=None):
        if title in self.notes:
            raise ValueError("Note already exists")
        self.notes[title] = {"content": content, "tags": tags or []}
        self.save_notes()

    def update_note(self, title, content, tags):
        if title in self.notes:
            self.notes[title] = {"content": content, "tags": tags}
            self.save_notes()

    def delete_note(self, title):
        if title in self.notes:
            del self.notes[title]
            self.save_notes()

    def filter_titles(self, query="", tag=None):
        query = query.lower()
        result = []
        for title, data in self.notes.items():
            matches_query = query in title.lower()
            matches_tag = tag is None or tag in data.get("tags", [])
            if matches_query and matches_tag:
                result.append(title)
        return result

class ModernButton(QPushButton):
    def __init__(self, text, primary=False, dark_theme=False):
        super().__init__(text)
        self.primary = primary
        self.dark_theme = dark_theme
        self.update_style()

    def update_style(self):
        if self.primary:
            if self.dark_theme:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 500;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #106ebe;
                    }
                    QPushButton:pressed {
                        background-color: #005a9e;
                    }
                """)
            else:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #007acc;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 500;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #005a9e;
                    }
                    QPushButton:pressed {
                        background-color: #004578;
                    }
                """)
        else:
            if self.dark_theme:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #3c3c3c;
                        color: #ffffff;
                        border: 1px solid #555;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 500;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #404040;
                        border-color: #666;
                    }
                    QPushButton:pressed {
                        background-color: #363636;
                    }
                """)
            else:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        color: #333;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 500;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #e8e8e8;
                        border-color: #bbb;
                    }
                    QPushButton:pressed {
                        background-color: #ddd;
                    }
                """)

    def set_theme(self, dark_theme):
        self.dark_theme = dark_theme
        self.update_style()

class NotesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Notes")
        self.resize(1200, 800)

        self.manager = NoteManager(NOTES_FILE)
        self.settings_manager = SettingsManager(SETTINGS_FILE)
        self.dark_theme = self.settings_manager.get_setting("dark_theme", False)
        self.current_note_title = None
        
        self.init_ui()
        self.apply_theme()

    def get_app_stylesheet(self, dark_theme=False):
        if dark_theme:
            return """
                QWidget {
                    font-family: 'Segoe UI', 'San Francisco', Arial, sans-serif;
                    font-size: 14px;
                    color: #ffffff;
                    background-color: #1e1e1e;
                }
                QLineEdit {
                    border: 2px solid #404040;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QLineEdit:focus {
                    border-color: #0078d4;
                    outline: none;
                }
                QComboBox {
                    border: 2px solid #404040;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    background-color: #2d2d2d;
                    color: #ffffff;
                    min-width: 120px;
                }
                QComboBox:focus {
                    border-color: #0078d4;
                }
                QComboBox::drop-down {
                    border: none;
                    background-color: #404040;
                }
                QComboBox QAbstractItemView {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    selection-background-color: #0078d4;
                }
                QListWidget {
                    border: 1px solid #404040;
                    border-radius: 8px;
                    background-color: #2d2d2d;
                    alternate-background-color: #323232;
                    selection-background-color: #0078d4;
                    selection-color: white;
                    outline: none;
                    color: #ffffff;
                }
                QListWidget::item {
                    padding: 12px 16px;
                    border-bottom: 1px solid #404040;
                    font-size: 14px;
                }
                QListWidget::item:hover {
                    background-color: #383838;
                }
                QListWidget::item:selected {
                    background-color: #0078d4;
                    color: white;
                }
                QTextEdit {
                    border: 1px solid #404040;
                    border-radius: 8px;
                    background-color: #2d2d2d;
                    color: #ffffff;
                    font-size: 14px;
                    line-height: 1.5;
                }
                QFrame {
                    background-color: #2d2d2d;
                    border-radius: 8px;
                }
                QLabel {
                    color: #cccccc;
                    font-weight: 500;
                }
            """
        else:
            return """
                QWidget {
                    font-family: 'Segoe UI', 'San Francisco', Arial, sans-serif;
                    font-size: 14px;
                    color: #333;
                    background-color: #fafafa;
                }
                QLineEdit {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border-color: #007acc;
                    outline: none;
                }
                QComboBox {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    background-color: white;
                    min-width: 120px;
                }
                QComboBox:focus {
                    border-color: #007acc;
                }
                QListWidget {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: white;
                    alternate-background-color: #f8f9fa;
                    selection-background-color: #007acc;
                    selection-color: white;
                    outline: none;
                }
                QListWidget::item {
                    padding: 12px 16px;
                    border-bottom: 1px solid #f0f0f0;
                    font-size: 14px;
                }
                QListWidget::item:hover {
                    background-color: #f0f8ff;
                }
                QListWidget::item:selected {
                    background-color: #007acc;
                    color: white;
                }
                QTextEdit {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: white;
                    font-size: 14px;
                    line-height: 1.5;
                }
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                }
                QLabel {
                    color: #666;
                    font-weight: 500;
                }
            """

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header with theme toggle
        header_layout = QHBoxLayout()
        header = QLabel("My Notes")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()

        # Theme toggle button
        self.theme_button = ModernButton("🌙 Dark", dark_theme=self.dark_theme)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setMaximumWidth(100)
        header_layout.addWidget(self.theme_button)

        main_layout.addLayout(header_layout)

        # Search and filter bar
        search_frame = QFrame()
        search_frame.setStyleSheet("QFrame { padding: 16px; margin-bottom: 8px; }")
        filter_layout = QHBoxLayout(search_frame)
        filter_layout.setSpacing(12)

        search_label = QLabel("Search:")
        search_label.setStyleSheet("QLabel { font-weight: 500; }")
        filter_layout.addWidget(search_label)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type to search notes...")
        self.search_bar.textChanged.connect(self.filter_notes)
        filter_layout.addWidget(self.search_bar, 2)

        tag_label = QLabel("Filter:")
        tag_label.setStyleSheet("QLabel { font-weight: 500; }")
        filter_layout.addWidget(tag_label)

        self.tag_filter = QComboBox()
        self.tag_filter.addItem("All Tags")
        self.tag_filter.currentTextChanged.connect(self.filter_notes)
        filter_layout.addWidget(self.tag_filter, 1)

        main_layout.addWidget(search_frame)

        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Notes list panel
        list_frame = QFrame()
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(16, 16, 16, 16)
        
        list_header = QLabel("Notes")
        list_header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 8px;
            }
        """)
        list_layout.addWidget(list_header)

        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.on_note_selected)
        self.notes_list.currentItemChanged.connect(self.on_note_selected)
        list_layout.addWidget(self.notes_list)

        # Control buttons for list
        list_controls = QHBoxLayout()
        self.new_button = ModernButton("+ New", primary=True, dark_theme=self.dark_theme)
        self.delete_button = ModernButton("Delete", dark_theme=self.dark_theme)
        
        self.new_button.clicked.connect(self.new_note)
        self.delete_button.clicked.connect(self.delete_note)
        
        list_controls.addWidget(self.new_button)
        list_controls.addStretch()
        list_controls.addWidget(self.delete_button)
        list_layout.addLayout(list_controls)

        splitter.addWidget(list_frame)

        # Editor panel
        editor_frame = QFrame()
        editor_layout = QVBoxLayout(editor_frame)
        editor_layout.setContentsMargins(16, 16, 16, 16)

        editor_header = QLabel("Editor")
        editor_header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 8px;
            }
        """)
        editor_layout.addWidget(editor_header)

        # Formatting toolbar
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("QFrame { border: 1px solid; border-radius: 8px; padding: 8px; margin-bottom: 8px; }")
        format_layout = QHBoxLayout(toolbar_frame)
        format_layout.setSpacing(8)

        # Format buttons
        self.bold_btn = ModernButton("B", dark_theme=self.dark_theme)
        self.bold_btn.setMaximumWidth(40)
        self.bold_btn.clicked.connect(lambda: self.set_format("bold"))
        
        self.italic_btn = ModernButton("I", dark_theme=self.dark_theme)
        self.italic_btn.setMaximumWidth(40)
        self.italic_btn.clicked.connect(lambda: self.set_format("italic"))
        
        self.underline_btn = ModernButton("U", dark_theme=self.dark_theme)
        self.underline_btn.setMaximumWidth(40)
        self.underline_btn.clicked.connect(lambda: self.set_format("underline"))

        # Font controls
        self.font_box = QComboBox()
        self.font_box.addItems(["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana"])
        self.font_box.setCurrentText("Arial")
        self.font_box.currentTextChanged.connect(self.set_font)

        self.size_box = QComboBox()
        self.size_box.addItems([str(s) for s in [10, 12, 14, 16, 18, 20, 24, 28]])
        self.size_box.setCurrentText("14")
        self.size_box.currentTextChanged.connect(lambda s: self.set_font_size(int(s)))

        self.color_btn = ModernButton("Color", dark_theme=self.dark_theme)
        self.color_btn.setMaximumWidth(60)
        self.color_btn.clicked.connect(self.set_color)

        format_layout.addWidget(self.bold_btn)
        format_layout.addWidget(self.italic_btn)
        format_layout.addWidget(self.underline_btn)
        format_layout.addWidget(QLabel("|"))  # Separator
        format_layout.addWidget(self.font_box)
        format_layout.addWidget(self.size_box)
        format_layout.addWidget(self.color_btn)
        format_layout.addStretch()

        editor_layout.addWidget(toolbar_frame)

        # Text editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Start typing your note here...")
        editor_layout.addWidget(self.editor)

        # Tags and save section
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("QFrame { border: 1px solid; border-radius: 8px; padding: 12px; }")
        bottom_layout = QVBoxLayout(bottom_frame)

        tag_row = QHBoxLayout()
        tag_label = QLabel("Tags:")
        tag_label.setStyleSheet("QLabel { font-weight: 500; }")
        tag_row.addWidget(tag_label)

        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter tags separated by commas (e.g., work, important, ideas)")
        tag_row.addWidget(self.tag_input)

        bottom_layout.addLayout(tag_row)

        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.save_button = ModernButton("Save Note", primary=True, dark_theme=self.dark_theme)
        self.save_button.clicked.connect(self.save_note)
        save_layout.addWidget(self.save_button)

        bottom_layout.addLayout(save_layout)
        editor_layout.addWidget(bottom_frame)

        splitter.addWidget(editor_frame)
        
        # Set splitter proportions
        splitter.setSizes([350, 650])
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)
        self.refresh_notes_list()
        self.select_first_note()

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.settings_manager.set_setting("dark_theme", self.dark_theme)
        self.apply_theme()

    def apply_theme(self):
        # Update main stylesheet
        self.setStyleSheet(self.get_app_stylesheet(self.dark_theme))
        
        # Update theme button text and icon
        if self.dark_theme:
            self.theme_button.setText("☀️ Light")
        else:
            self.theme_button.setText("🌙 Dark")
        
        # Update all ModernButton instances
        buttons = [
            self.new_button, self.delete_button, self.save_button,
            self.bold_btn, self.italic_btn, self.underline_btn, self.color_btn, self.theme_button
        ]
        
        for button in buttons:
            button.set_theme(self.dark_theme)

        # Update header color
        if self.dark_theme:
            header_color = "#ffffff"
            toolbar_border_color = "#404040"
            bottom_border_color = "#404040"
        else:
            header_color = "#333"
            toolbar_border_color = "#e0e0e0"
            bottom_border_color = "#e0e0e0"

        # Find and update header labels
        for widget in self.findChildren(QLabel):
            if widget.text() in ["My Notes", "Notes", "Editor"]:
                current_style = widget.styleSheet()
                if "font-size: 24px" in current_style:
                    widget.setStyleSheet(f"""
                        QLabel {{
                            font-size: 24px;
                            font-weight: 600;
                            color: {header_color};
                            margin-bottom: 10px;
                        }}
                    """)
                elif "font-size: 16px" in current_style:
                    widget.setStyleSheet(f"""
                        QLabel {{
                            font-size: 16px;
                            font-weight: 600;
                            color: {header_color};
                            margin-bottom: 8px;
                        }}
                    """)

        # Update frame borders
        for frame in self.findChildren(QFrame):
            current_style = frame.styleSheet()
            if "border: 1px solid;" in current_style:
                if "padding: 8px" in current_style:
                    frame.setStyleSheet(f"QFrame {{ border: 1px solid {toolbar_border_color}; border-radius: 8px; padding: 8px; margin-bottom: 8px; }}")
                elif "padding: 12px" in current_style:
                    frame.setStyleSheet(f"QFrame {{ border: 1px solid {bottom_border_color}; border-radius: 8px; padding: 12px; }}")

    def refresh_notes_list(self, filtered_titles=None):
        self.notes_list.clear()
        
        # Update tag filter
        self.tag_filter.blockSignals(True)
        current_tag = self.tag_filter.currentText()
        self.tag_filter.clear()
        self.tag_filter.addItem("All Tags")

        all_tags = set()
        note_titles = (
            filtered_titles if filtered_titles is not None else self.manager.get_titles()
        )
        
        for title in sorted(note_titles, key=str.lower):
            item = QListWidgetItem(title)
            self.notes_list.addItem(item)
            all_tags.update(self.manager.get_note(title).get("tags", []))

        # Restore tag filter selection
        for tag in sorted(all_tags):
            self.tag_filter.addItem(tag)
        
        # Try to restore previous tag selection
        tag_index = self.tag_filter.findText(current_tag)
        if tag_index >= 0:
            self.tag_filter.setCurrentIndex(tag_index)
        
        self.tag_filter.blockSignals(False)

    def filter_notes(self):
        query = self.search_bar.text()
        selected_tag = self.tag_filter.currentText()
        
        tag = None if selected_tag == "All Tags" else selected_tag
        filtered = self.manager.filter_titles(query, tag)
        self.refresh_notes_list(filtered)

    def new_note(self):
        title, ok = QInputDialog.getText(self, "New Note", "Enter note title:")
        if ok and title.strip():
            title = title.strip()
            try:
                self.manager.add_note(title)
                self.current_note_title = title
                self.editor.clear()
                self.tag_input.clear()
                self.refresh_notes_list()
                self.select_note_in_list(title)
                self.editor.setFocus()  # Focus on editor for immediate typing
            except ValueError:
                QMessageBox.warning(self, "Error", f"Note '{title}' already exists.")

    def save_note(self):
        if self.current_note_title:
            content = self.editor.toHtml()
            tags = [t.strip() for t in self.tag_input.text().split(",") if t.strip()]
            self.manager.update_note(self.current_note_title, content, tags)
            self.refresh_notes_list()
            
            # Show brief save confirmation
            self.save_button.setText("Saved!")
            QApplication.processEvents()
            
            # Reset button text after a short delay
            def reset_save_button():
                self.save_button.setText("Save Note")
            
            # Simple timer alternative using QApplication
            import threading
            threading.Timer(1.0, reset_save_button).start()
        else:
            QMessageBox.information(self, "No Note Selected", "Please select or create a note first.")

    def delete_note(self):
        if self.current_note_title:
            reply = QMessageBox.question(
                self, "Delete Note", 
                f"Are you sure you want to delete '{self.current_note_title}'?\n\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.manager.delete_note(self.current_note_title)
                self.editor.clear()
                self.tag_input.clear()
                self.current_note_title = None
                self.refresh_notes_list()
                self.select_first_note()
        else:
            QMessageBox.information(self, "No Note Selected", "Please select a note to delete.")

    def on_note_selected(self, item):
        """Fixed method to handle note selection properly"""
        if item is None:
            return
            
        # Handle both QListWidgetItem (from click) and item change events
        if hasattr(item, 'text'):
            title = item.text()
        else:
            return
            
        # Only load if it's a different note
        if title != self.current_note_title:
            self.load_note_content(title)

    def load_note_content(self, title):
        """Load note content into editor"""
        self.current_note_title = title
        note_data = self.manager.get_note(title)
        
        # Load content
        content = note_data.get("content", "")
        if content:
            self.editor.setHtml(content)
        else:
            self.editor.clear()
        
        # Load tags
        tags = note_data.get("tags", [])
        self.tag_input.setText(", ".join(tags))

    def select_note_in_list(self, title):
        """Select a specific note in the list"""
        for i in range(self.notes_list.count()):
            item = self.notes_list.item(i)
            if item.text() == title:
                self.notes_list.setCurrentItem(item)
                self.load_note_content(title)
                break

    def select_first_note(self):
        """Select the first note if any exist"""
        if self.notes_list.count() > 0:
            first_item = self.notes_list.item(0)
            self.notes_list.setCurrentItem(first_item)
            self.load_note_content(first_item.text())

    # Rich text formatting methods
    def set_format(self, fmt_type):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()

        if fmt_type == "bold":
            weight = QFont.Bold if cursor.charFormat().fontWeight() != QFont.Bold else QFont.Normal
            fmt.setFontWeight(weight)
        elif fmt_type == "italic":
            italic = not cursor.charFormat().fontItalic()
            fmt.setFontItalic(italic)
        elif fmt_type == "underline":
            underline = not cursor.charFormat().fontUnderline()
            fmt.setFontUnderline(underline)

        cursor.mergeCharFormat(fmt)
        self.editor.setFocus()

    def set_font(self, font_name):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontFamily(font_name)
        cursor.mergeCharFormat(fmt)
        self.editor.setFocus()

    def set_font_size(self, size):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        cursor.mergeCharFormat(fmt)
        self.editor.setFocus()

    def set_color(self):
        color = QColorDialog.getColor(Qt.black, self, "Choose Text Color")
        if color.isValid():
            cursor = self.editor.textCursor()
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            cursor.mergeCharFormat(fmt)
            self.editor.setFocus()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = NotesApp()
    window.show()
    sys.exit(app.exec_())