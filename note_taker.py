from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QWidget,
    QFileDialog,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys
import json

class WebpageNoteTaker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Webpage Note Taker")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.layout = QVBoxLayout()

        # Webpage Viewer
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.example.com"))  # Default webpage
        self.layout.addWidget(self.browser)

        # Note Area
        self.note_area = QTextEdit()
        self.note_area.setPlaceholderText("Type your notes here...")
        self.layout.addWidget(self.note_area)

        # Save Note Button
        save_button = QPushButton("Save Note")
        save_button.clicked.connect(self.save_note)
        self.layout.addWidget(save_button)

        # View Notes Button
        view_notes_button = QPushButton("View Notes")
        view_notes_button.clicked.connect(self.view_notes)
        self.layout.addWidget(view_notes_button)

        # Export Notes Button
        export_button = QPushButton("Export Notes")
        export_button.clicked.connect(self.export_notes)
        self.layout.addWidget(export_button)

        # Set central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def save_note(self):
        """
        Save either highlighted text or manually entered notes tied to the current URL.
        """
        def capture_selection(js_result):
            note_text = js_result.strip() or self.note_area.toPlainText()
            if note_text:
                current_url = self.browser.url().toString()
                with open("notes.txt", "a") as file:
                    file.write(f"URL: {current_url}\nNote: {note_text}\n\n")
                self.note_area.clear()
                print("Note saved!")
            else:
                print("No text selected or entered.")

        # Execute JavaScript to get highlighted text, fallback to manual entry
        self.browser.page().runJavaScript("window.getSelection().toString()", capture_selection)

    def view_notes(self):
        """
        Display saved notes in a new window.
        """
        try:
            with open("notes.txt", "r") as file:
                notes = file.read()
        except FileNotFoundError:
            notes = "No notes saved yet."

        # Display notes in a new QTextEdit window
        notes_window = QMainWindow(self)
        notes_window.setWindowTitle("Saved Notes")
        notes_area = QTextEdit()
        notes_area.setText(notes)
        notes_area.setReadOnly(True)
        notes_window.setCentralWidget(notes_area)
        notes_window.setGeometry(150, 150, 600, 400)
        notes_window.show()

    def export_notes(self):
        """
        Export notes to a JSON file.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Notes", "", "JSON Files (*.json)", options=options
        )
        if file_name:
            try:
                with open("notes.txt", "r") as file:
                    raw_notes = file.readlines()
                notes_data = []
                current_note = {}
                for line in raw_notes:
                    if line.startswith("URL:"):
                        if current_note:
                            notes_data.append(current_note)
                        current_note = {"url": line.replace("URL:", "").strip()}
                    elif line.startswith("Note:"):
                        current_note["note"] = line.replace("Note:", "").strip()
                if current_note:
                    notes_data.append(current_note)
                with open(file_name, "w") as json_file:
                    json.dump(notes_data, json_file, indent=4)
                print("Notes exported successfully.")
            except Exception as e:
                print(f"Error exporting notes: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebpageNoteTaker()
    window.show()
    sys.exit(app.exec_())
