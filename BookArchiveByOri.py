import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QAction, QToolBar, QVBoxLayout, QWidget, QLabel,
                             QScrollArea, QLineEdit, QHBoxLayout, QCheckBox, QStatusBar, QMessageBox, QFileDialog, QDialog, QGroupBox, QGridLayout, QShortcut, QFontComboBox, QComboBox, QPushButton )
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtMultimedia import QSound
import os
import tinytag
import re
import random
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MusicHandler")
        self.setGeometry(100, 100, 1500, 900)

        # Creating status bar object
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        # Setting text in status bar
        self.status_bar.showMessage("סטטוס: מוכן")

        self.center_label = None
        self.input_fields_layout = None
        self.layout = None
        self.drag_area = None
        self.year, self.track_number, self.contributing_artists, self.album_artist, self.title, self.file_name = None, None, None, None, None, None

        self.audio_files_paths = []   # Contains all the paths of the audio files displayed in the software
        self.new_file_paths = []
        self.new1_file_paths = []
        self.input_fields = []
        self.previous_names = {}

        self.initui()

    def initui(self):
        # Creating a widget for GUI components
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setAcceptDrops(True)  # אפשר גרירה על האובייקט הראשי
        central_widget.dragEnterEvent = self.dragEnterEvent
        central_widget.dragLeaveEvent = self.dragLeaveEvent
        central_widget.dropEvent = self.dropEvent
        # Creating the main frame/tunnel
        self.layout = QVBoxLayout(central_widget)

        self.create_bars()
        self.add_sarching()
        self.create_check_boxes()
        self.creating_a_frame_with_a_scroll_bar()

        self.show()

    def create_bars(self):
        # create a menu bar
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("קובץ")

        open_folder_action = QAction("בחר מתיקייה", self)
        open_folder_action.triggered.connect(self.open_file)
        file_menu.addAction(open_folder_action)

        exit_action = QAction("יציאה", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menu_bar.addMenu("כלים")
        Manage_json_files_action = QAction("נהל קבצי json", self)
        Manage_json_files_action.triggered.connect(self.manage_json_files)
        tools_menu.addAction(Manage_json_files_action)

        self.setMenuBar(menu_bar)

        # create toolbar
        tool_bar = QToolBar("סרגל כלים", self)
        self.addToolBar(tool_bar)
        # create the save button
        save_action = QAction(QIcon(r'dependence\images\save.png'), 'שמור (Ctrl+S)', self)
        # Create a shortcut for Ctrl+S and Ctrl+ד
        save_shortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        save_shortcut.activated.connect(self.save_action_triggered)
        save_shortcut_heb = QShortcut(QKeySequence('Ctrl+ד'), self)
        save_shortcut_heb.activated.connect(self.save_action_triggered)

        save_action.triggered.connect(self.save_action_triggered)
        tool_bar.addAction(save_action)
        # create the clean all button
        clear_action = QAction(QIcon(r'dependence\images\clear.png'), "נקה הכל", self)
        clear_action.triggered.connect(self.clear_action_triggered)
        tool_bar.addAction(clear_action)
        # create the back button
        back_action = QAction(QIcon(r'dependence\images\back.png'), "חזור", self)
        # Create a shortcut for Ctrl+S and Ctrl+ד
        back_shortcut = QShortcut(QKeySequence('Ctrl+Z'), self)
        back_shortcut.activated.connect(self.restore_names_triggered)
        back_shortcut_heb = QShortcut(QKeySequence('Ctrl+ז'), self)
        back_shortcut_heb.activated.connect(self.restore_names_triggered)

        back_action.triggered.connect(self.restore_names_triggered)
        tool_bar.addAction(back_action)


    def add_sarching(self):
        # יצירת קופסת קבוצתית
        group_box = QGroupBox("מנוע חיפוש", self)

        grid_layout = QGridLayout(group_box)

        frame_2 = QWidget(group_box)
        grid_layout.addWidget(frame_2, 1, 1)

        grid_layout_4 = QGridLayout(frame_2)

        # שדה כמות בארכיון
        self.line_edit_amount_in_archive = QLineEdit(frame_2)
        self.line_edit_amount_in_archive.textChanged.connect(self.start_search)
        self.line_edit_amount_in_archive.setObjectName("lineEdit_13")
        self.line_edit_amount_in_archive.setPlaceholderText("הזן כמות בארכיון")
        grid_layout_4.addWidget(self.line_edit_amount_in_archive, 1, 6, 1, 1)

        # שדה כמות מושאלת
        self.line_edit_borrowed_amount = QLineEdit(frame_2)
        self.line_edit_borrowed_amount.textChanged.connect(self.start_search)
        self.line_edit_borrowed_amount.setObjectName("lineEdit_6")
        self.line_edit_borrowed_amount.setPlaceholderText("כמות מושאלת")
        grid_layout_4.addWidget(self.line_edit_borrowed_amount, 1, 5, 1, 1)

        # שדה מצב הספר
        self.book_condition_combo_box = QComboBox(frame_2)
        self.book_condition_combo_box.addItem("בחר מצב ספר")
        self.book_condition_combo_box.addItem("חדש")
        self.book_condition_combo_box.addItem("משומש")
        self.book_condition_combo_box.addItem("פתור/כתוב")
        self.book_condition_combo_box.addItem("קרוע")
        self.book_condition_combo_box.addItem("לא ידוע")
        self.book_condition_combo_box.currentIndexChanged.connect(self.start_search)
        self.book_condition_combo_box.setObjectName("fontComboBox_2")
        self.book_condition_combo_box.setPlaceholderText("בחר מצב ספר")
        grid_layout_4.addWidget(self.book_condition_combo_box, 1, 4, 1, 1)

        # שדה תאריך השאלה
        self.line_edit_loaning_date = QLineEdit(frame_2)
        self.line_edit_loaning_date.textChanged.connect(self.start_search)
        self.line_edit_loaning_date.setObjectName("lineEdit_9")
        self.line_edit_loaning_date.setPlaceholderText("הזן תאריך השאלה")
        grid_layout_4.addWidget(self.line_edit_loaning_date, 1, 3, 1, 1)

        # שדה סוג הספר
        self.book_type_combo_box = QComboBox(frame_2)
        self.book_type_combo_box.addItem("בחר סוג ספר")
        self.book_type_combo_box.addItem("קודש")
        self.book_type_combo_box.addItem("כתיבה")
        self.book_type_combo_box.addItem("קריאה")
        self.book_type_combo_box.currentIndexChanged.connect(self.start_search)
        self.book_type_combo_box.setObjectName("fontComboBox")
        self.book_type_combo_box.setPlaceholderText("בחר סוג ספר")
        grid_layout_4.addWidget(self.book_type_combo_box, 1, 2, 1, 1)

        # שדה שם השואל
        self.line_edit_borrower_name = QLineEdit(frame_2)
        self.line_edit_borrower_name.textChanged.connect(self.start_search)
        self.line_edit_borrower_name.setObjectName("lineEdit_10")
        self.line_edit_borrower_name.setPlaceholderText("הזן שם השואל")
        grid_layout_4.addWidget(self.line_edit_borrower_name, 1, 1, 1, 1)

        # שדה הערות
        self.line_edit_remarks = QLineEdit(frame_2)
        self.line_edit_remarks.textChanged.connect(self.start_search)
        self.line_edit_remarks.setObjectName("lineEdit_4")
        self.line_edit_remarks.setPlaceholderText("הזן הערות (אם יש)")
        grid_layout_4.addWidget(self.line_edit_remarks, 1, 0, 1, 1)

        frame = QWidget(group_box)
        grid_layout.addWidget(frame, 0, 1)

        grid_layout_3 = QGridLayout(frame)

        # שדה מזהה הספר
        self.line_edit_book_id = QLineEdit(frame)
        self.line_edit_book_id.textChanged.connect(self.start_search)
        self.line_edit_book_id.setObjectName("lineEdit")
        self.line_edit_book_id.setPlaceholderText("הזן מזהה הספר")
        grid_layout_3.addWidget(self.line_edit_book_id, 1, 7, 1, 1)

        # שדה שם הספר
        self.line_edit_book_title = QLineEdit(frame)
        self.line_edit_book_title.textChanged.connect(self.start_search)
        self.line_edit_book_title.setObjectName("lineEdit")
        self.line_edit_book_title.setPlaceholderText("הזן שם הספר")
        grid_layout_3.addWidget(self.line_edit_book_title, 1, 6, 1, 1)

        # שדה שם הסדרה
        self.line_edit_series_name = QLineEdit(frame)
        self.line_edit_series_name.textChanged.connect(self.start_search)
        self.line_edit_series_name.setObjectName("lineEdit_2")
        self.line_edit_series_name.setPlaceholderText("הזן שם הסדרה")
        grid_layout_3.addWidget(self.line_edit_series_name, 1, 5, 1, 1)

        # שדה חלק בסדרה
        self.line_edit_series_part = QLineEdit(frame)
        self.line_edit_series_part.textChanged.connect(self.start_search)
        self.line_edit_series_part.setObjectName("lineEdit_12")
        self.line_edit_series_part.setPlaceholderText("הזן חלק בסדרה")
        grid_layout_3.addWidget(self.line_edit_series_part, 1, 4, 1, 1)

        # שדה מחבר
        self.line_edit_author = QLineEdit(frame)
        self.line_edit_author.textChanged.connect(self.start_search)
        self.line_edit_author.setObjectName("lineEdit_author")
        self.line_edit_author.setPlaceholderText("הזן מחבר")
        grid_layout_3.addWidget(self.line_edit_author, 1, 3, 1, 1)

        # שדה מוציא לאור
        self.line_edit_publisher = QLineEdit(frame)
        self.line_edit_publisher.textChanged.connect(self.start_search)
        self.line_edit_publisher.setObjectName("lineEdit_author")
        self.line_edit_publisher.setPlaceholderText("הזן מוציא לאור")
        grid_layout_3.addWidget(self.line_edit_publisher, 1, 2, 1, 1)

        # שדה מדף
        self.line_edit_shelf = QLineEdit(frame)
        self.line_edit_shelf.textChanged.connect(self.start_search)
        self.line_edit_shelf.setObjectName("lineEdit_11")
        self.line_edit_shelf.setPlaceholderText("הזן מדף")
        grid_layout_3.addWidget(self.line_edit_shelf, 1, 1, 1, 1)

        # הוספת הרכיבים לממשק המשתמש שלך
        self.layout.addWidget(group_box)
    def create_check_boxes(self):
        self.check_boxes_layout = QHBoxLayout()
        self.layout.addLayout(self.check_boxes_layout)
        check_box_names = ["הערות", "שם השואל", "סוג הספר", "תאריך", "מצב", "מושאל", "כמות בארכיון", "מדף", "מוציא לאור", "מחבר", "חלק בסדרה", "שם הסדרה", "שם הספר", "מזהה", "כלים"]
        self.check_boxes = []
        for name in check_box_names:
            if name == "שם הקובץ":
                label = QLabel(name, self)
                self.check_boxes_layout.addWidget(label)
            else:
                label = QLabel(name, self)
                self.check_boxes_layout.addWidget(label)

    def start_search(self):
        # Retrieve the text from all the QLineEdit widgets
        self.amount_in_archive = self.line_edit_amount_in_archive.text()
        self.borrowed_amount = self.line_edit_borrowed_amount.text()
        self.book_condition = self.book_condition_combo_box.currentText()
        self.loaning_date = self.line_edit_loaning_date.text()
        self.book_type = self.book_type_combo_box.currentText()
        self.borrower_name = self.line_edit_borrower_name.text()
        self.remarks = self.line_edit_remarks.text()
        self.book_id = self.line_edit_book_id.text()
        self.book_title = self.line_edit_book_title.text()
        self.series_name = self.line_edit_series_name.text()
        self.series_part = self.line_edit_series_part.text()
        self.author = self.line_edit_author.text()
        self.publisher = self.line_edit_publisher.text()
        self.shelf = self.line_edit_shelf.text()

        # Print the retrieved text to the console
        # print("book id:", self.book_id)
        # print("book title:", self.book_title)
        # print("book type:", self.book_type)
        # print("series name:", self.series_name)
        # print("Series Part:", self.series_part)
        # print("Shelf:", self.shelf)
        # print("amount in archive:", self.amount_in_archive)
        # print("Books Borrowed:", self.borrowed_amount)
        # print("borrower name:", self.borrower_name)
        # print("loaning date:", self.loaning_date)
        # print("book condition:", self.book_condition)
        # print("Author:", self.author)
        # print("Publisher:", self.publisher)
        # print("remarks:", self.remarks)
        self.load_archive()

    def load_archive(self):
        self.clearLayout(self.input_fields_layout)

        archive_path = os.path.join("dependence", "ArcFiles", "archive.json")
        with open(archive_path, "r", encoding="utf-8") as file:
            self.data = json.load(file)

        for book in self.data.get("books", []):
            row_layout = QHBoxLayout()  # יצירת אובייקט עבור שורה חדשה

            keys = list(book.keys())  # Get all keys as a list
            second_key = keys[0]  # Get the second key
            print("Second Key:", second_key)
            if self.remarks in keys[0]:
                print(self.remarks)

            if (
                    (self.book_id == "" or self.book_id in book["book_id"]) and
                    (self.book_title == "" or self.book_title in book["book_title"]) and
                    (self.book_type == "בחר סוג ספר" or self.book_type in book["book_type"]) and
                    (self.author == "" or self.author in book["author"]) and
                    (self.publisher == "" or self.publisher in book["publisher"]) and
                    (self.series_name == "" or self.series_name in book["series_name"]) and
                    (self.series_part == "" or self.series_part in book["series_part"]) and
                    (self.borrowed_amount == "" or self.borrowed_amount in book["borrowed_amount"]) and
                    (self.borrower_name == "" or self.borrower_name in book["borrower_name"]) and
                    (self.loaning_date == "" or self.loaning_date in book["loaning_date"]) and
                    (self.shelf == "" or self.shelf in book["shelf"]) and
                    (self.amount_in_archive == "" or self.amount_in_archive in book["amount_in_archive"]) and
                    (self.book_condition == "בחר מצב ספר" or self.book_condition in book["book_condition"]) and
                    (self.remarks == "" or self.remarks in book["remarks"])
            ):
                print("הצלחתי!!!!!!!!!!!")

                # רשימת המידע שברצונך ליצור QLineEdit לכל פריט בה
                data_to_display = [
                    book["remarks"],
                    book["borrower_name"],
                    book["book_type"],
                    book["loaning_date"],
                    book["book_condition"],
                    book["borrowed_amount"],
                    book["amount_in_archive"],
                    book["shelf"],
                    book["publisher"],
                    book["author"],
                    book["series_part"],
                    book["series_name"],
                    book["book_title"],
                    book["book_id"]
                ]

                for data in data_to_display:
                    edit_line = QLineEdit(data, self)
                    edit_line.setReadOnly(True)
                    row_layout.addWidget(edit_line)

                # הוסף את הכפתור והצמיד אירוע חיצוני לו כדי להדפיס את book_id
                self.edit_button = QPushButton('E', self)
                self.edit_button.setFixedSize(20, 20)
                self.edit_button.clicked.connect(lambda state, book_id=book["book_id"]: self.print_book_id(book_id))
                row_layout.addWidget(self.edit_button)

            self.input_fields_layout.addLayout(row_layout)
        self.Add_a_label_to_the_frame()

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.clearLayout(item.layout())

    def print_book_id(self, book_id):
        print("Book ID:", book_id)



    def creating_a_frame_with_a_scroll_bar(self):
        # Creating a frame for the song details with a scroll bar
        scroll_area = QScrollArea(self)
        self.layout.addWidget(scroll_area)
        scroll_content = QWidget(scroll_area)
        scroll_area.setWidget(scroll_content)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidgetResizable(True)

        self.input_fields_layout = QVBoxLayout()
        scroll_layout.addLayout(self.input_fields_layout)

    def Add_a_label_to_the_frame(self):
        # יצירת והוספת ה- QLabel ל- input_fields_layout
        self.center_label = QLabel("", self)
        self.center_label.setAlignment(QtCore.Qt.AlignCenter)  # מיון הטקסט למרכז
        # הגדרת גופן גדול יותר לטקסט
        font = QFont()
        font.setPointSize(20)  # גודל הגופן בנקודות
        self.center_label.setFont(font)
        self.input_fields_layout.addWidget(self.center_label)

# So far the initial interface has been designed
# From here on, mainly the functions of the software operations

    def manage_json_files(self):
        pass

    def open_file(self):
        pass

    def dragLeaveEvent(self, event):
        pass

    def dragEnterEvent(self, event):
        pass

    def dropEvent(self, event):
        pass

# So far the songs are placed in the window and the software alerts you to anything that is needed
# From here on, the buttons actions

    def save_action_triggered(self):
        pass

    def clear_action_triggered(self):
        pass

    def restore_names_triggered(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
