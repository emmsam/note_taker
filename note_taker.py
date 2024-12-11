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
import sqlite3
import json
from datetime import datetime


class WebpageNoteTaker(QMainWindow):
    def __init__(self):
        """
        Initialize the Webpage Note Taker application.
        This sets up the main window, layout, and database connection.
        """
        super().__init__()
        self.initUI()
        self.initDatabase()

    def initUI(self):
        """
        Set up the user interface for the application.
        Includes a browser, note-taking area, and buttons for various actions.
        """
        self.setWindowTitle("Webpage Note Taker")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.layout = QVBoxLayout()

        # Webpage Viewer
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.example.com"))  # Convert string to QUrl
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

    def initDatabase(self):
        """
        Initialize the SQLite database and create a notes table if it doesn't exist.
        """
        self.conn = sqlite3.connect("notes.db")  # Connect to a database file (creates it if it doesn't exist)
        self.cursor = self.conn.cursor()

        # Create a table for notes
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            note TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()  # Save changes

    def save_note(self):
        """
        Save either the highlighted text or manually entered note into the database.
        """
        def capture_selection(js_result):
            note_text = js_result.strip() or self.note_area.toPlainText()
            if note_text:  # Ensure there's something to save
                current_url = self.browser.url().toString()  # Get the current webpage URL
                # Insert the note into the database
                self.cursor.execute("INSERT INTO notes (url, note) VALUES (?, ?)", (current_url, note_text))
                self.conn.commit()  # Save the changes
                self.note_area.clear()  # Clear the note area
                print("Note saved to database!")
            else:
                print("No text selected or entered.")

        # Capture selected text from the webpage or fallback to manual entry
        self.browser.page().runJavaScript("window.getSelection().toString()", capture_selection)

    def view_notes(self):
        """
        Display all saved notes from the database in a new window.
        """
        self.cursor.execute("SELECT url, note, timestamp FROM notes ORDER BY timestamp DESC")
        notes = self.cursor.fetchall()  # Fetch all notes from the database

        if notes:
            notes_text = "\n".join(
                f"URL: {url}\nNote: {note}\nTimestamp: {timestamp}\n{'-' * 40}" for url, note, timestamp in notes
            )
        else:
            notes_text = "No notes saved yet."

        # Display notes in a new QTextEdit window
        notes_window = QMainWindow(self)
        notes_window.setWindowTitle("Saved Notes")
        notes_area = QTextEdit()
        notes_area.setText(notes_text)
        notes_area.setReadOnly(True)  # Make the text area read-only
        notes_window.setCentralWidget(notes_area)
        notes_window.setGeometry(150, 150, 600, 400)
        notes_window.show()

    def export_notes(self):
        """
        Export all notes from the database to a JSON file.
        """
        # Open a file dialog to select where to save the JSON file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Notes", "", "JSON Files (*.json)", options=options
        )
        if file_name:
            self.cursor.execute("SELECT url, note, timestamp FROM notes")
            notes = self.cursor.fetchall()  # Fetch all notes

            # Convert notes to a list of dictionaries
            notes_data = [
                {"url": url, "note": note, "timestamp": timestamp} for url, note, timestamp in notes
            ]

            # Save the notes as a JSON file
            with open(file_name, "w") as json_file:
                json.dump(notes_data, json_file, indent=4)
            print("Notes exported successfully.")

    def closeEvent(self, event):
        """
        Override the closeEvent to ensure the database connection is closed properly.
        """
        self.conn.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebpageNoteTaker()
    window.show()
    sys.exit(app.exec_())
