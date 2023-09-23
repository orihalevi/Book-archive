import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QAction, QToolBar, QVBoxLayout, QWidget, QLabel,
                             QScrollArea, QLineEdit, QHBoxLayout, QCheckBox, QStatusBar, QMessageBox, QFileDialog, QDialog, QGroupBox, QGridLayout, QShortcut, QFontComboBox, QComboBox, QPushButton )
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QIntValidator, QPixmap
from PyQt5.QtMultimedia import QSound
import os
import tinytag
import re
import random
import json
import datetime

def read_archive_json():
    archive_path = "dependence/ArcFiles/archive.json"
    with open(archive_path, "r", encoding="utf-8") as file:
        all_books_data = json.load(file)
        return all_books_data

# פונקציה למחיקת ספר לפי ה-ID
def delete_book_by_id(books_ids):
    dialog3 = are_you_sure_window(books_ids)
    dialog3.exec_()

    if dialog3.data:
        data = read_archive_json()
        for id in books_ids:
            # מצא את הספר ברשימת הספרים לפי ה-ID
            for book in data["books"]:
                if id == book['book_id']:
                    # מחק את הספר מהרשימה
                    data["books"].remove(book)
                    break  # אחרי שמחקנו את הספר, אין טעם להמשיך לחפש

            # שמור את המידע חזרה לקובץ JSON
            with open('dependence/ArcFiles/archive.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.group_boxes_to_clear = []
        self.group_boxes = []
        self.g = 0
        self.borrower_id = ""
        self.book_id = ""
        self.book_title = ""
        self.series_name = ""
        self.series_part = ""
        self.grade = ""
        self.age_group = ""
        self.author = ""
        self.publisher = ""
        self.shelf = ""
        self.amount_in_archive = ""
        self.is_borrowed = ""
        self.book_condition = ""
        self.loaning_date = ""
        self.book_type = ""
        self.borrower_name = ""
        self.remarks = ""

        self.setWindowTitle("BookArchiveByOri")
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
        add_books_action = QAction(QIcon(r'dependence\images\add_books.png'), 'הוסף ספרים', self)
        # Create a shortcut for Ctrl+S and Ctrl+ד
        #add_books_shortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        #add_books_shortcut.activated.connect(self.add_books_action_triggered)
        #add_books_shortcut_heb = QShortcut(QKeySequence('Ctrl+ד'), self)
        #add_books_shortcut_heb.activated.connect(self.add_books_action_triggered)

        add_books_action.triggered.connect(self.add_books_action_triggered)
        tool_bar.addAction(add_books_action)
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

        # שדה מדף
        self.line_edit_shelf = QLineEdit(frame_2)
        self.line_edit_shelf.textChanged.connect(self.start_search)
        self.line_edit_shelf.setObjectName("lineEdit_11")
        self.line_edit_shelf.setPlaceholderText("הזן מדף")
        grid_layout_4.addWidget(self.line_edit_shelf, 1, 8, 1, 1)

        # שדה כמות בארכיון
        self.line_edit_amount_in_archive = QLineEdit(frame_2)
        self.line_edit_amount_in_archive.textChanged.connect(self.start_search)
        self.line_edit_amount_in_archive.setObjectName("lineEdit_13")
        self.line_edit_amount_in_archive.setPlaceholderText("הזן כמות בארכיון")
        grid_layout_4.addWidget(self.line_edit_amount_in_archive, 1, 7, 1, 1)

        # שדה כמות מושאלת
        self.line_edit_is_borrowed = QLineEdit(frame_2)
        self.line_edit_is_borrowed.textChanged.connect(self.start_search)
        self.line_edit_is_borrowed.setObjectName("lineEdit_6")
        self.line_edit_is_borrowed.setPlaceholderText("כמות מושאלת")
        grid_layout_4.addWidget(self.line_edit_is_borrowed, 1, 6, 1, 1)

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
        grid_layout_4.addWidget(self.book_condition_combo_box, 1, 5, 1, 1)

        # שדה תאריך השאלה
        self.line_edit_loaning_date = QLineEdit(frame_2)
        self.line_edit_loaning_date.textChanged.connect(self.start_search)
        self.line_edit_loaning_date.setObjectName("lineEdit_9")
        self.line_edit_loaning_date.setPlaceholderText("הזן תאריך השאלה")
        grid_layout_4.addWidget(self.line_edit_loaning_date, 1, 4, 1, 1)

        # שדה סוג הספר
        self.book_type_combo_box = QComboBox(frame_2)
        self.book_type_combo_box.addItem("בחר סוג ספר")
        self.book_type_combo_box.addItem("קודש")
        self.book_type_combo_box.addItem("כתיבה")
        self.book_type_combo_box.addItem("קריאה")
        self.book_type_combo_box.addItem("לימוד")
        self.book_type_combo_box.currentIndexChanged.connect(self.start_search)
        self.book_type_combo_box.setObjectName("fontComboBox")
        self.book_type_combo_box.setPlaceholderText("בחר סוג ספר")
        grid_layout_4.addWidget(self.book_type_combo_box, 1, 3, 1, 1)

        # שדה שם השואל/הלוקח
        self.line_edit_borrower_name = QLineEdit(frame_2)
        self.line_edit_borrower_name.textChanged.connect(self.start_search)
        self.line_edit_borrower_name.setObjectName("lineEdit_10")
        self.line_edit_borrower_name.setPlaceholderText("הזן שם השואל/הלוקח")
        grid_layout_4.addWidget(self.line_edit_borrower_name, 1, 2, 1, 1)

        # שדה תעודת זהות השואל
        self.line_edit_borrower_id = QLineEdit(frame_2)
        self.line_edit_borrower_id.textChanged.connect(self.start_search)
        self.line_edit_borrower_id.setObjectName("lineEdit_4")
        self.line_edit_borrower_id.setPlaceholderText("הזן תעודת זהות השואל")
        grid_layout_4.addWidget(self.line_edit_borrower_id, 1, 1, 1, 1)

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

        # שדה כיתה
        self.line_edit_grade = QLineEdit(frame)
        self.line_edit_grade.textChanged.connect(self.start_search)
        self.line_edit_grade.setObjectName("lineEdit_grade")
        self.line_edit_grade.setPlaceholderText("הזן כיתה")
        grid_layout_3.addWidget(self.line_edit_grade, 1, 3, 1, 1)

        # שדה שכבת גיל
        self.line_edit_age_group = QLineEdit(frame)
        self.line_edit_age_group.textChanged.connect(self.start_search)
        self.line_edit_age_group.setObjectName("lineEdit_age_group")
        self.line_edit_age_group.setPlaceholderText("הזן שכבת גיל")
        grid_layout_3.addWidget(self.line_edit_age_group, 1, 2, 1, 1)

        # שדה מחבר
        self.line_edit_author = QLineEdit(frame)
        self.line_edit_author.textChanged.connect(self.start_search)
        self.line_edit_author.setObjectName("lineEdit_author")
        self.line_edit_author.setPlaceholderText("הזן מחבר")
        grid_layout_3.addWidget(self.line_edit_author, 1, 1, 1, 1)

        # שדה מוציא לאור
        self.line_edit_publisher = QLineEdit(frame)
        self.line_edit_publisher.textChanged.connect(self.start_search)
        self.line_edit_publisher.setObjectName("lineEdit_author")
        self.line_edit_publisher.setPlaceholderText("הזן מוציא לאור")
        grid_layout_3.addWidget(self.line_edit_publisher, 1, 0, 1, 1)


        # הוספת הרכיבים לממשק המשתמש שלך
        self.layout.addWidget(group_box)
        self.creating_a_frame_with_a_scroll_bar()
        self.load_archive()

    def start_search(self):
        # Retrieve the text from all the QLineEdit widgets
        self.remarks = self.line_edit_remarks.text()
        self.borrower_id = self.line_edit_borrower_id.text()
        self.borrower_name = self.line_edit_borrower_name.text()
        self.book_type = self.book_type_combo_box.currentText()
        self.loaning_date = self.line_edit_loaning_date.text()
        self.book_condition = self.book_condition_combo_box.currentText()
        self.is_borrowed = self.line_edit_is_borrowed.text()
        self.amount_in_archive = self.line_edit_amount_in_archive.text()
        self.shelf = self.line_edit_shelf.text()
        self.publisher = self.line_edit_publisher.text()
        self.author = self.line_edit_author.text()
        self.age_group = self.line_edit_age_group.text()
        self.grade = self.line_edit_grade.text()
        self.series_part = self.line_edit_series_part.text()
        self.series_name = self.line_edit_series_name.text()
        self.book_title = self.line_edit_book_title.text()
        self.book_id = self.line_edit_book_id.text()

        self.load_archive()

    def load_archive(self):

        self.count_books_with_conditions()
        if self.g >= 1:
            for gr in self.group_boxes_to_clear:
                layout = gr.layout()
                if layout is not None:
                    if layout.count() >= 1:
                        while layout.count():
                            item = layout.takeAt(0)
                            if item.widget():
                                try:
                                    item.widget().deleteLater()
                                except:
                                    print("4")
                    else:
                        print("adsasd")

        self.g += 1

        """
        self.clearLayout(self.input_fields_layout)

        self.data = read_archive_json()

        for book in self.data.get("books", []):
            row_layout = QHBoxLayout()  # יצירת אובייקט עבור שורה חדשה

            keys = list(book.keys())  # Get all keys as a list
            second_key = keys[0]  # Get the second key

            if (
                    (self.book_id == "" or self.book_id in book["book_id"]) and
                    (self.book_title == "" or self.book_title in book["book_title"]) and
                    (self.book_type == "בחר סוג ספר" or self.book_type in book["book_type"]) and
                    (self.author == "" or self.author in book["author"]) and
                    (self.publisher == "" or self.publisher in book["publisher"]) and
                    (self.series_name == "" or self.series_name in book["series_name"]) and
                    (self.series_part == "" or self.series_part in book["series_part"]) and
                    (self.grade == "" or self.grade in book["grade"]) and
                    (self.age_group == "" or self.age_group in book["age_group"]) and
                    (self.is_borrowed == "" or self.is_borrowed in book["is_borrowed"]) and
                    (self.borrower_name == "" or self.borrower_name in book["borrower_name"]) and
                    (self.loaning_date == "" or self.loaning_date in book["loaning_date"]) and
                    (self.shelf == "" or self.shelf in book["shelf"]) and
                    (self.amount_in_archive == "" or self.amount_in_archive in book["amount_in_archive"]) and
                    (self.book_condition == "בחר מצב ספר" or self.book_condition in book["book_condition"]) and
                    (self.borrower_id == "" or self.borrower_id in book["borrower_id"]) and
                    (self.remarks == "" or self.remarks in book["remarks"])
            ):

                # רשימת המידע שברצונך ליצור QLineEdit לכל פריט בה
                data_to_display = [
                    book["remarks"],
                    book["borrower_id"],
                    book["borrower_name"],
                    book["book_type"],
                    book["loaning_date"],
                    book["book_condition"],
                    book["is_borrowed"],
                    book["amount_in_archive"],
                    book["shelf"],
                    book["publisher"],
                    book["author"],
                    book["age_group"],
                    book["grade"],
                    book["series_part"],
                    book["series_name"],
                    book["book_title"],
                    book["book_id"]
                ]

                for i, data in enumerate(data_to_display):
                    edit_line = QLineEdit(data, self)
                    edit_line.setReadOnly(True)
                    row_layout.addWidget(edit_line)

                    # בדוק האם זהו ה-QLineEdit החמישי בשורה
                    if i == 6:
                        if data == "כן":
                            edit_line.setStyleSheet("background-color: #EF9A9A;")
                        elif data == "לא":
                            edit_line.setStyleSheet("background-color: #C5E1A5;")

                # הוסף את הכפתור והצמיד אירוע חיצוני לו כדי להדפיס את book_id
                self.edit_button = QPushButton(QIcon(r'dependence\images\book_setting.png'), '', self)
                self.edit_button.setStyleSheet('background-color: transparent; border: 1px solid #d0d0d0; border-radius: 3px;')
                self.edit_button.setFixedSize(20, 20)
                self.edit_button.clicked.connect(lambda state, book_id=book["book_id"]: self.edit_book_data(book_id))
                row_layout.addWidget(self.edit_button)

            self.input_fields_layout.addLayout(row_layout)
        self.Add_a_label_to_the_frame()
        """




        self.data = read_archive_json()
        # הוסף lineedit עבור כל שם ספר לתוך ה groupBox "שם הספר"
        for book in self.data.get("books", []):
            if (
                    (self.book_id == "" or self.book_id in book["book_id"]) and
                    (self.book_title == "" or self.book_title in book["book_title"]) and
                    (self.book_type == "בחר סוג ספר" or self.book_type in book["book_type"]) and
                    (self.author == "" or self.author in book["author"]) and
                    (self.publisher == "" or self.publisher in book["publisher"]) and
                    (self.series_name == "" or self.series_name in book["series_name"]) and
                    (self.series_part == "" or self.series_part in book["series_part"]) and
                    (self.grade == "" or self.grade in book["grade"]) and
                    (self.age_group == "" or self.age_group in book["age_group"]) and
                    (self.is_borrowed == "" or self.is_borrowed in book["is_borrowed"]) and
                    (self.borrower_name == "" or self.borrower_name in book["borrower_name"]) and
                    (self.loaning_date == "" or self.loaning_date in book["loaning_date"]) and
                    (self.shelf == "" or self.shelf in book["shelf"]) and
                    (self.amount_in_archive == "" or self.amount_in_archive in book["amount_in_archive"]) and
                    (self.book_condition == "בחר מצב ספר" or self.book_condition in book["book_condition"]) and
                    (self.borrower_id == "" or self.borrower_id in book["borrower_id"]) and
                    (self.remarks == "" or self.remarks in book["remarks"])
            ):

                data_to_display = [
                    book["remarks"],
                    book["borrower_id"],
                    book["borrower_name"],
                    book["book_type"],
                    book["loaning_date"],
                    book["book_condition"],
                    book["is_borrowed"],
                    book["amount_in_archive"],
                    book["shelf"],
                    book["publisher"],
                    book["author"],
                    book["age_group"],
                    book["grade"],
                    book["series_part"],
                    book["series_name"],
                    book["book_title"],
                    book["book_id"]
                ]


                # פתח את הקובץ JSON
                with open('dependence/ArcFiles/archive.json', 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                for i, data in enumerate(data_to_display):
                    edit_line = QLineEdit(data, self)
                    edit_line.setReadOnly(True)
                    edit_line.setToolTip(str(self.group_boxes[i].title()) + ": " + str(data))
                    self.group_boxes[i].layout().addWidget(edit_line)

                    # בדוק האם זהו ה-QLineEdit החמישי בשורה
                    if i == 6:
                        if data == "כן":
                            edit_line.setStyleSheet("background-color: #EF9A9A;")
                        elif data == "לא":
                            edit_line.setStyleSheet("background-color: #C5E1A5;")


                # Creating a book_setting button
                edit_button = QPushButton(QIcon(r'dependence\images\book_setting.png'), '')
                edit_button.setStyleSheet(
                    'background-color: transparent; border: 1px solid #d0d0d0; border-radius: 3px;')
                edit_button.setFixedSize(21, 21)
                edit_button.clicked.connect(lambda state, book_id=book["book_id"]: self.edit_book_data(book_id))
                self.group_boxes[17].layout().addWidget(edit_button)

        for group_box in self.group_boxes:
            name_label = QLabel("")
            name_label.setAlignment(QtCore.Qt.AlignTop)
            group_box.layout().addWidget(name_label)
    #  "A function that returns the numerical amount of books in which the key values book_title, series_name,
    #  series_part, grade, age_group, author, and publisher are all the same."
    def count_books_with_conditions(self):
        books_group = []

        books_data = read_archive_json()

        # יצירת משתנה לשמירת מספר הספרים התואמים את התנאים
        count = 0

        # לולאה עבור כל ספר ברשימה
        for book in books_data["books"]:
            if book["book_id"] not in books_group:
                books_group = []
                common_book_title = book["book_title"]
                common_series_name = book["series_name"]
                common_series_part = book["series_part"]
                common_grade = book["grade"]
                common_age_group = book["age_group"]
                common_author = book["author"]
                common_publisher = book["publisher"]
                # אם הערכים המשותפים בין כל הספרים שונים מהספר הראשון, הספר אינו עומד בתנאים
                for book in books_data["books"]:
                    if (
                        common_book_title == book["book_title"]
                        and common_series_name == book["series_name"]
                        and common_series_part == book["series_part"]
                        and common_grade == book["grade"]
                        and common_age_group == book["age_group"]
                        and common_author == book["author"]
                        and common_publisher == book["publisher"]
                    ):
                        if book["book_id"] not in books_group:
                            books_group.append(book["book_id"])
                            count += 1
                    else:
                        continue
                books_data1 = read_archive_json()
                # לולאה עבור כל ספר ברשימת הספרים
                for book in books_data1["books"]:
                    if book["book_id"] in books_group:
                        book["amount_in_archive"] = str(count)
                # לאחר שעשינו את השינויים בספרים, נשמור את הקובץ מחדש
                with open("dependence/ArcFiles/archive.json", "w", encoding="utf-8") as json_file:
                    json.dump(books_data1, json_file, ensure_ascii=False, indent=4)
                count = 0


    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.clearLayout(item.layout())

    # בפונקציה edit_book_data במקום הקריאה לפונקציה print_book_id תקרא לפונקציה שמייצרת את החלון החדש
    def edit_book_data(self, book_id):
        # חפש את הספר לפי ה book_id
        selected_book = None
        for book in self.data.get("books", []):
            if book["book_id"] == book_id:
                selected_book = book
                break
        if selected_book:
            book_data = [
                selected_book["book_id"],
                selected_book["book_title"],
                selected_book["series_name"],
                selected_book["series_part"],
                selected_book["grade"],
                selected_book["age_group"],
                selected_book["author"],
                selected_book["publisher"],
                selected_book["shelf"],
                selected_book["amount_in_archive"],
                selected_book["is_borrowed"],
                selected_book["book_condition"],
                selected_book["loaning_date"],
                selected_book["book_type"],
                selected_book["borrower_name"],
                selected_book["borrower_id"],
                selected_book["remarks"]
            ]

            self.open_settings_dialog(book_data)

    # פונקציה שתפתח את הדיאלוג עם העריכה
    def open_settings_dialog(self, book_data):
        dialog1 = SettingsDialog(book_data)
        dialog1.exec_()
        self.load_archive()


    def creating_a_frame_with_a_scroll_bar(self):
        # Creating a frame for the song details with a scroll bar
        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")


        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 1539, 507))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")

        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.splitter = QtWidgets.QSplitter(self.scrollAreaWidgetContents_3)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.splitter_2 = QtWidgets.QSplitter(self.splitter)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setOpaqueResize(True)
        self.splitter_2.setChildrenCollapsible(False)
        self.splitter_2.setObjectName("splitter_2")

        self.groupBox_remarks = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_remarks.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_remarks.setFlat(True)
        self.groupBox_remarks.setObjectName("groupBox_remarks")
        self.groupBox_remarks.setTitle("הערות")
        self.group_boxes.append(self.groupBox_remarks)

        self.gridLayout_13 = QtWidgets.QGridLayout(self.groupBox_remarks)
        self.gridLayout_13.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.group_boxes_to_clear.append(self.gridLayout_13)

        self.groupBox_borrower_id = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_borrower_id.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_borrower_id.setFlat(True)
        self.groupBox_borrower_id.setObjectName("groupBox_borrower_id")
        self.groupBox_borrower_id.setTitle("תעודת זהות")
        self.group_boxes.append(self.groupBox_borrower_id)

        self.gridLayout_12 = QtWidgets.QGridLayout(self.groupBox_borrower_id)
        self.gridLayout_12.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.group_boxes_to_clear.append(self.gridLayout_12)

        self.groupBox_borrower_name = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_borrower_name.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_borrower_name.setFlat(True)
        self.groupBox_borrower_name.setObjectName("groupBox_borrower_name")
        self.groupBox_borrower_name.setTitle("שם השואל/הלוקח")
        self.group_boxes.append(self.groupBox_borrower_name)

        self.gridLayout_11 = QtWidgets.QGridLayout(self.groupBox_borrower_name)
        self.gridLayout_11.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.group_boxes_to_clear.append(self.gridLayout_11)

        self.groupBox_book_type = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_book_type.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_book_type.setFlat(True)
        self.groupBox_book_type.setObjectName("groupBox_book_type")
        self.groupBox_book_type.setTitle("סוג הספר")
        self.group_boxes.append(self.groupBox_book_type)

        self.gridLayout_10 = QtWidgets.QGridLayout(self.groupBox_book_type)
        self.gridLayout_10.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.group_boxes_to_clear.append(self.gridLayout_10)

        self.groupBox_loaning_date = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_loaning_date.setEnabled(True)
        self.groupBox_loaning_date.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_loaning_date.setFlat(True)
        self.groupBox_loaning_date.setObjectName("groupBox_loaning_date")
        self.groupBox_loaning_date.setTitle("תאריך השאלה")
        self.group_boxes.append(self.groupBox_loaning_date)

        self.gridLayout_9 = QtWidgets.QGridLayout(self.groupBox_loaning_date)
        self.gridLayout_9.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.group_boxes_to_clear.append(self.gridLayout_9)

        self.groupBox_6 = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_6.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_6.setFlat(True)
        self.groupBox_6.setObjectName("groupBox_6")
        self.groupBox_6.setTitle("מצב הספר")
        self.group_boxes.append(self.groupBox_6)

        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_8.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.group_boxes_to_clear.append(self.gridLayout_8)

        self.groupBox_is_borrowed = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_is_borrowed.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox_is_borrowed.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_is_borrowed.setFlat(True)
        self.groupBox_is_borrowed.setObjectName("groupBox_is_borrowed")
        self.groupBox_is_borrowed.setTitle("מושאל")
        self.group_boxes.append(self.groupBox_is_borrowed)

        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_is_borrowed)
        self.gridLayout_7.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.group_boxes_to_clear.append(self.gridLayout_7)

        self.groupBox_amount_in_archive = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_amount_in_archive.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_amount_in_archive.setFlat(True)
        self.groupBox_amount_in_archive.setObjectName("groupBox_amount_in_archive")
        self.groupBox_amount_in_archive.setTitle("כמות בארכיון")
        self.group_boxes.append(self.groupBox_amount_in_archive)

        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_amount_in_archive)
        self.gridLayout_6.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.group_boxes_to_clear.append(self.gridLayout_6)

        self.groupBox_shelf = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_shelf.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_shelf.setFlat(True)
        self.groupBox_shelf.setObjectName("groupBox_shelf")
        self.groupBox_shelf.setTitle("מדף")
        self.group_boxes.append(self.groupBox_shelf)

        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_shelf)
        self.gridLayout_5.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.group_boxes_to_clear.append(self.gridLayout_5)

        self.groupBox_publisher = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_publisher.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_publisher.setFlat(True)
        self.groupBox_publisher.setObjectName("groupBox_publisher")
        self.groupBox_publisher.setTitle("מוציא לאור")
        self.group_boxes.append(self.groupBox_publisher)

        self.gridLayout_15 = QtWidgets.QGridLayout(self.groupBox_publisher)
        self.gridLayout_15.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.group_boxes_to_clear.append(self.gridLayout_15)

        self.groupBox_author = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_author.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_author.setFlat(True)
        self.groupBox_author.setObjectName("groupBox_author")
        self.groupBox_author.setTitle("מחבר")
        self.group_boxes.append(self.groupBox_author)

        self.gridLayout_14 = QtWidgets.QGridLayout(self.groupBox_author)
        self.gridLayout_14.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.group_boxes_to_clear.append(self.gridLayout_14)

        self.groupBox_age_group = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_age_group.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_age_group.setFlat(True)
        self.groupBox_age_group.setObjectName("groupBox_age_group")
        self.groupBox_age_group.setTitle("שכבת גיל")
        self.group_boxes.append(self.groupBox_age_group)

        self.gridLayout_17 = QtWidgets.QGridLayout(self.groupBox_age_group)
        self.gridLayout_17.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_17.setObjectName("gridLayout_17")
        self.group_boxes_to_clear.append(self.gridLayout_17)

        self.groupBox_grade = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_grade.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_grade.setFlat(True)
        self.groupBox_grade.setObjectName("groupBox_grade")
        self.groupBox_grade.setTitle("כיתה")
        self.group_boxes.append(self.groupBox_grade)

        self.gridLayout_16 = QtWidgets.QGridLayout(self.groupBox_grade)
        self.gridLayout_16.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_16.setObjectName("gridLayout_16")
        self.group_boxes_to_clear.append(self.gridLayout_16)

        self.groupBox_series_part = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_series_part.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_series_part.setFlat(True)
        self.groupBox_series_part.setObjectName("groupBox_series_part")
        self.groupBox_series_part.setTitle("חלק בסדרה")
        self.group_boxes.append(self.groupBox_series_part)

        self.gridLayout_18 = QtWidgets.QGridLayout(self.groupBox_series_part)
        self.gridLayout_18.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_18.setObjectName("gridLayout_18")
        self.group_boxes_to_clear.append(self.gridLayout_18)

        self.groupBox_series_name = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_series_name.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_series_name.setFlat(True)
        self.groupBox_series_name.setObjectName("groupBox_series_name")
        self.groupBox_series_name.setTitle("שם הסדרה")
        self.group_boxes.append(self.groupBox_series_name)

        self.gridLayout_19 = QtWidgets.QGridLayout(self.groupBox_series_name)
        self.gridLayout_19.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_19.setObjectName("gridLayout_19")
        self.group_boxes_to_clear.append(self.gridLayout_19)

        self.groupBox_book_title = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_book_title.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_book_title.setFlat(True)
        self.groupBox_book_title.setObjectName("groupBox_book_title")
        self.groupBox_book_title.setTitle("שם הספר")
        self.group_boxes.append(self.groupBox_book_title)

        self.gridLayout_20 = QtWidgets.QGridLayout(self.groupBox_book_title)
        self.gridLayout_20.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_20.setObjectName("gridLayout_20")
        self.group_boxes_to_clear.append(self.gridLayout_20)

        self.groupBox_book_id = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_book_id.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_book_id.setFlat(True)
        self.groupBox_book_id.setObjectName("groupBox_book_id")
        self.groupBox_book_id.setTitle("מזהה")
        self.group_boxes.append(self.groupBox_book_id)

        self.gridLayout_21 = QtWidgets.QGridLayout(self.groupBox_book_id)
        self.gridLayout_21.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_21.setObjectName("gridLayout_21")
        self.group_boxes_to_clear.append(self.gridLayout_21)

        self.groupBox_tools = QtWidgets.QGroupBox(self.splitter_2)
        self.groupBox_tools.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_tools.setFlat(True)
        self.groupBox_tools.setObjectName("groupBox_tools")
        self.groupBox_tools.setTitle("כלים")
        self.group_boxes.append(self.groupBox_tools)

        self.gridLayout_22 = QtWidgets.QGridLayout(self.groupBox_tools)
        self.gridLayout_22.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_22.setObjectName("gridLayout_22")
        self.group_boxes_to_clear.append(self.gridLayout_22)

        self.gridLayout_2.addWidget(self.splitter, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)


        self.layout.addWidget(self.scrollArea)
        #scroll_content = QWidget(self.scrollArea)
        #self.scrollArea.setWidget(scroll_content)
        #scroll_layout = QVBoxLayout(scroll_content)
        self.scrollArea.setWidgetResizable(True)


        self.input_fields_layout = QVBoxLayout()
        #scroll_layout.addLayout(self.input_fields_layout)

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

    def add_books_action_triggered(self):
        dialog1 = AddBooksWindow()
        dialog1.exec_()
        self.load_archive()

    def clear_action_triggered(self):
        pass

    def restore_names_triggered(self):
        pass

class EditBookDialog(QDialog):
    def __init__(self, book_data):
        super().__init__()
        self.this_original_book_id = book_data[0]
        self.setWindowTitle(f"עריכת ספר  {self.this_original_book_id}")
        self.setGeometry(700, 300, 400, 300)

        layout = QVBoxLayout()

        # רשימה לשמירת ה-QLineEdit וה-QComboBox
        self.input_widgets = []

        # רשימה של שמות התוויות בסדר שאתה רוצה
        labels_names = [
            "מזהה ספר (לא מומלץ לשנות):",
            "כותרת הספר:",
            "שם הסדרה:",
            "חלק בסדרה:",
            "כיתה:",
            "קבוצת גיל:",
            "מְחַבֵּר:",
            "מוֹצִיא לָאוֹר:",
            "מַדָף:",
            "כמות בארכיון:",
            "סכום שאול:",
            "מצב הספר:",
            "תאריך ההשאלה:",
            "סוג הספר:",
            "שם השואל/הלוקח:",
            "תעודת זהות:",
            "הערות:"
        ]

        # הלולאה הולכת על כל רכיב ברשימה
        for key, value in enumerate(book_data):
            # יצירת QLabel עם השם המתאים מהרשימה
            if key == 0:
                label = QLabel(labels_names[key])
                label.setStyleSheet("color: red;")

            else:
                label = QLabel(labels_names[key])

            # אם השדה הוא "book_type" או "book_condition", יוצר QComboBox ויתחבר לפעולה הנדרשת
            if key not in [13, 11, 0]:
                # אם המפתח הוא לא "book_type" או "book_condition", ייצור QLineEdit והוספתו ל־layout
                edit_line = QLineEdit(value)
                # יצירת QHBoxLayout והוספת התווית וה־LineEdit אליו
                row_layout = QHBoxLayout()
                row_layout.addWidget(edit_line)
                row_layout.addWidget(label)
                # הוספת ה־HBoxLayout ל־layout הראשי
                layout.addLayout(row_layout)
                self.input_widgets.append(edit_line)
            elif key == 0:
                edit_line = QLineEdit(value)
                edit_line.setReadOnly(False)
                # יצירת QHBoxLayout והוספת התווית וה־LineEdit אליו
                row_layout = QHBoxLayout()
                row_layout.addWidget(edit_line)
                row_layout.addWidget(label)
                # הוספת ה־HBoxLayout ל־layout הראשי
                layout.addLayout(row_layout)
                self.input_widgets.append(edit_line)
            elif key == 11:
                # יצירת QComboBox והוספתו ל־layout
                combo_box = QComboBox()
                combo_box.addItem(value)
                combo_box.addItem("בחר מצב ספר")
                combo_box.addItem("חדש")
                combo_box.addItem("משומש")
                combo_box.addItem("פתור/כתוב")
                combo_box.addItem("קרוע")
                combo_box.addItem("לא ידוע")
                # יצירת QHBoxLayout והוספת התווית וה־ComboBox אליו
                row_layout = QHBoxLayout()
                row_layout.addWidget(combo_box)
                row_layout.addWidget(label)
                # הוספת ה־HBoxLayout ל־layout הראשי
                layout.addLayout(row_layout)
                self.input_widgets.append(combo_box)
            elif key == 13:
                # יצירת QComboBox והוספתו ל־layout
                combo_box = QComboBox()
                combo_box.addItem(value)
                combo_box.addItem("בחר סוג ספר")
                combo_box.addItem("קודש")
                combo_box.addItem("כתיבה")
                combo_box.addItem("קריאה")
                combo_box.addItem("לימוד")
                # יצירת QHBoxLayout והוספת התווית וה־ComboBox אליו
                row_layout = QHBoxLayout()
                row_layout.addWidget(combo_box)
                row_layout.addWidget(label)
                # הוספת ה־HBoxLayout ל־layout הראשי
                layout.addLayout(row_layout)
                self.input_widgets.append(combo_box)

        # אחרי שיצרנו את כל ה-QLineEdit וה-QComboBox, נוסיף את הרשימה שלהם לערכה של self.edited_data

        self.setLayout(layout)

        # ניתן להוסיף את הכפתורים שאתה רוצה כאן, לדוגמה, כפתורי "שמור" ו"בטל"
        # יצירת כפתור "שמור"
        save_button = QPushButton("שמור", self)
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)

        # יצירת כפתור "בטל"
        cancel_button = QPushButton("בטל", self)
        cancel_button.clicked.connect(self.cancel_button_clicked)
        layout.addWidget(cancel_button)


    # פונקציה שתוסיף את הערך החדש ל־self.input_widgets
    def add_current_text_to_(self):
        new_value = self.book_type_combo_box.currentText()
        # בדוק האם הערך כבר קיים ב־self.input_widgets
        if new_value not in [widget.text() for widget in self.input_widgets]:
            self.input_widgets.append(new_value)

    def cancel_button_clicked(self):
        print("ssssss")

    def save_changes(self):
        # אני מניח שבניית המידע על הספר תתבצע בדיוק באותה הסדר כמו שהוצגה בעמודה הימנית
        # הקבלת מערך עם ה-LineEdits המעודכנים

        self.edited_data = [widget.text() if isinstance(widget, QLineEdit) else widget.currentText() for widget in self.input_widgets]
        #(self.edited_data)

        # בניית מילון עם שמות השדות כמפתחות וערכי השדות מה-LineEdits כערכים
        book_data = {
            "remarks": self.edited_data[16],
            "borrower_id": self.edited_data[15],
            "borrower_name": self.edited_data[14],
            "book_type": self.edited_data[13],
            "loaning_date": self.edited_data[12],
            "book_condition": self.edited_data[11],
            "is_borrowed": self.edited_data[10],
            "amount_in_archive": self.edited_data[9],
            "shelf": self.edited_data[8],
            "publisher": self.edited_data[7],
            "author": self.edited_data[6],
            "age_group": self.edited_data[5],
            "grade": self.edited_data[4],
            "series_part": self.edited_data[3],
            "series_name": self.edited_data[2],
            "book_title": self.edited_data[1],
            "book_id": self.edited_data[0]
        }

        # כאן תוכל להוסיף קוד שמעדכן את המידע בקובץ JSON
        # נניח שיש לך מערך של הספרים ב- self.data ואתה רוצה לעדכן את המידע במערך זה על פי book_id
        # אפשר לעשות משהו כמו זה:


        self.data = read_archive_json()
        for i, book in enumerate(self.data["books"]):
            if book["book_id"] == self.this_original_book_id:

                if self.edited_data[0] != self.this_original_book_id:
                    data1 = read_archive_json()
                    # עבור על כל הספרים ברשימה
                    for book in data1["books"]:
                        if book["book_id"] == self.edited_data[0]:
                            book_data["book_id"] = self.this_original_book_id
                            # הודעת השגיאה
                            error_message = f"המזהה החדש שבחרת הינו כבר בשימוש ע\"י ספר אחר,\nשינוי המזהה {self.this_original_book_id} לא עבר בהצלחה"
                            # חלון הודעת שגיאה
                            error_box = QtWidgets.QMessageBox()
                            error_box.setIcon(QtWidgets.QMessageBox.Critical)
                            error_box.setWindowTitle("שגיאה")
                            error_box.setText(error_message)

                            # הצגת ההודעה למשתמש
                            error_box.exec_()

                self.data["books"][i] = book_data
                break


        # כאן תוכל לשמור את המידע המעודכן לקובץ JSON שוב
        archive_path = os.path.join("dependence", "ArcFiles", "archive.json")
        with open(archive_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

        # כאן תוכל לסגור את הדיאלוג
        self.accept()


class AddBooksWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # יצירת כל הווידג'טים

        self.title_label = QLabel("שם הספר:")
        self.title_lineedit = QLineEdit()

        self.series_label = QLabel("שם הסדרה:")
        self.series_lineedit = QLineEdit()

        self.series_part_label = QLabel("חלק בסדרה:")
        self.series_part_lineedit = QLineEdit()

        self.grade_label = QLabel("כיתה:")
        self.grade_lineedit = QLineEdit()

        self.age_group_label = QLabel("שכבת גיל:")
        self.age_group_lineedit = QLineEdit()

        self.author_label = QLabel("מחבר:")
        self.author_lineedit = QLineEdit()

        self.publisher_label = QLabel("מוציא לאור:")
        self.publisher_lineedit = QLineEdit()

        self.shelf_label = QLabel("מדף:")
        self.shelf_lineedit = QLineEdit()

        self.book_status_label = QLabel("מצב הספר:")
        self.book_status_combobox = QComboBox()
        self.book_status_combobox.addItems(["בחר מצב ספר", "חדש", "משומש", "פתור/כתוב", "קרוע", "לא ידוע"])

        self.book_type_label = QLabel("סוג הספר:")
        self.book_type_combobox = QComboBox()
        self.book_type_combobox.addItems(["בחר סוג ספר", "קודש", "כתיבה", "קריאה", "לימוד"])

        self.remarks_label = QLabel("הערות:")
        self.remarks_lineedit = QLineEdit()

        self.amount_label = QLabel("כמות:")
        self.amount_lineedit = QLineEdit()
        # הגבלת הקלט לספרות בלבד
        amount_validator = QIntValidator()
        self.amount_lineedit.setValidator(amount_validator)

        # יצירת כפתור "שמור"
        self.save_button = QPushButton("שמור")
        self.save_button.clicked.connect(self.save_button_clicked)

        # הפריכה של כל הווידג'טים בתוך מסגרת בעזרת QVBoxLayout
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_lineedit)
        layout.addWidget(self.series_label)
        layout.addWidget(self.series_lineedit)
        layout.addWidget(self.series_part_label)
        layout.addWidget(self.series_part_lineedit)
        layout.addWidget(self.grade_label)
        layout.addWidget(self.grade_lineedit)
        layout.addWidget(self.age_group_label)
        layout.addWidget(self.age_group_lineedit)
        layout.addWidget(self.author_label)
        layout.addWidget(self.author_lineedit)
        layout.addWidget(self.publisher_label)
        layout.addWidget(self.publisher_lineedit)
        layout.addWidget(self.shelf_label)
        layout.addWidget(self.shelf_lineedit)
        layout.addWidget(self.book_status_label)
        layout.addWidget(self.book_status_combobox)
        layout.addWidget(self.book_type_label)
        layout.addWidget(self.book_type_combobox)
        layout.addWidget(self.remarks_label)
        layout.addWidget(self.remarks_lineedit)
        layout.addWidget(self.amount_label)
        layout.addWidget(self.amount_lineedit)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.setWindowTitle("הוספת ספרים")
        self.setGeometry(700, 300, 400, 300)


    def create_new_books(self):
        data = read_archive_json()
        # יצור אובייקט חדש לספר
        new_book = {
            "remarks": self.remarks,
            "book_condition": self.book_condition,
            "amount_in_archive": "",
            "shelf": self.shelf,
            "loaning_date": "",
            "borrower_name": "",
            "borrower_id": "",
            "is_borrowed": "לא",
            "series_part": self.series_part,
            "series_name": self.series_name,
            "publisher": self.publisher,
            "author": self.author,
            "age_group": self.age_group,
            "grade": self.grade,
            "book_type": self.book_type,
            "book_title": self.book_title,
            "book_id": self.book_id
        }

        # הוסף את הספר החדש לרשימת הספרים בקובץ JSON
        data['books'].append(new_book)

        # שמור את הקובץ בחזרה
        with open('dependence/ArcFiles/archive.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def save_button_clicked(self):
        # פונקציה ליצירת מספר רנדומלי בעל 5 ספרות
        def generate_random_number():
            return str(random.randint(10000, 99999))

        # פונקציה לבדיקה אם המספר קיים בקובץ JSON
        def is_number_exists(number, data):
            books_ids = []
            for book in data['books']:
                books_ids.append(book['book_id'])
            # לולאה שמבצעת את הבדיקה
            for books_id in books_ids:
                if str(books_id) == str(number):
                    return True
            return False

        self.amount = self.amount_lineedit.text()
        if self.amount == "":
            self.amount = 1
        for _ in range(int(self.amount)):

            data = read_archive_json()
            while True:
                random_number = generate_random_number()
                if not is_number_exists(random_number, data):
                    break

            self.remarks = self.remarks_lineedit.text().strip()
            self.book_type = self.book_type_combobox.currentText().strip()
            self.book_condition = self.book_status_combobox.currentText().strip()
            self.shelf = self.shelf_lineedit.text().strip()
            self.publisher = self.publisher_lineedit.text().strip()
            self.author = self.author_lineedit.text().strip()
            self.age_group = self.age_group_lineedit.text().strip()
            self.grade = self.grade_lineedit.text().strip()
            self.series_part = self.series_part_lineedit.text().strip()
            self.series_name = self.series_lineedit.text().strip()
            self.book_title = self.title_lineedit.text().strip()
            self.book_id = str(random_number)

            self.create_new_books()

        self.close()


class SettingsDialog(QDialog):
    def __init__(self, book_data):
        super().__init__()

        self.initUI(book_data)

    def initUI(self, book_data):
        # יצירת כל הווידג'טים
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        self.frame = QtWidgets.QFrame(self)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.delete_book_button = QtWidgets.QPushButton(self.frame)
        self.delete_book_button.setGeometry(QtCore.QRect(20, 20, 150, 150))
        self.delete_book_button.setObjectName("delete_book_button")
        self.delete_book_button.setText("")  # הטקסט יוסר לגמרי
        self.delete_book_button.clicked.connect(lambda: self.delete_this_book(book_data))
        #self.delete_book_button.clicked.connect(lambda state, book_id=book_data[0]: self.delete_this_book(book_id))
        # קביעת רקע כתמונה
        self.delete_book_button_pixmap = QPixmap('dependence/images/delete_book.png')
        self.delete_book_button.setIconSize(self.delete_book_button.size())
        self.delete_book_button.setIcon(QIcon(self.delete_book_button_pixmap))

        self.duplicate_book_button = QtWidgets.QPushButton(self.frame)
        self.duplicate_book_button.setGeometry(QtCore.QRect(225, 20, 150, 150))
        self.duplicate_book_button.setObjectName("duplicate_book_button")
        self.duplicate_book_button.setText("")  # הטקסט יוסר לגמרי
        #self.edit_book_button.clicked.connect(lambda: self.open_edit_dialog(book_data))
        # קביעת רקע כתמונה
        self.duplicate_book_button_pixmap = QPixmap('dependence/images/add_book.png')
        self.duplicate_book_button.setIconSize(self.duplicate_book_button.size())
        self.duplicate_book_button.setIcon(QIcon(self.duplicate_book_button_pixmap))

        self.Borrow_book_button = QtWidgets.QPushButton(self.frame)
        self.Borrow_book_button.setGeometry(QtCore.QRect(430, 20, 150, 150))
        self.Borrow_book_button.setObjectName("Borrow_book_button")
        self.Borrow_book_button.setText("")  # הטקסט יוסר לגמרי
        self.Borrow_book_button.clicked.connect(lambda: self.lend_or_return_book(book_data))
        # self.edit_book_button.clicked.connect(lambda: self.open_edit_dialog(book_data))
        # קביעת רקע כתמונה
        self.Borrow_book_button_pixmap = QPixmap('dependence/images/nook_return.png')
        self.Borrow_book_button.setIconSize(self.Borrow_book_button.size())
        self.Borrow_book_button.setIcon(QIcon(self.Borrow_book_button_pixmap))

        if book_data[10] == "לא":
            self.Borrow_book_button_pixmap = QPixmap('dependence/images/book_lend.png')
            self.Borrow_book_button.setIconSize(self.Borrow_book_button.size())
            self.Borrow_book_button.setIcon(QIcon(self.Borrow_book_button_pixmap))

        self.edit_book_button = QtWidgets.QPushButton(self.frame)
        self.edit_book_button.setGeometry(QtCore.QRect(635, 20, 150, 150))
        self.edit_book_button.setObjectName("edit_book_button")
        self.edit_book_button.setText("")  # הטקסט יוסר לגמרי
        self.edit_book_button.clicked.connect(lambda: self.open_edit_dialog(book_data))
        # קביעת רקע כתמונה
        self.edit_book_button_pixmap = QPixmap('dependence/images/edit_book.png')
        self.edit_book_button.setIconSize(self.edit_book_button.size())
        self.edit_book_button.setIcon(QIcon(self.edit_book_button_pixmap))

        SButtons = [
            self.delete_book_button,
            self.duplicate_book_button,
            self.Borrow_book_button,
            self.edit_book_button
        ]

        for i in SButtons:
            i.setStyleSheet(
                "QPushButton {"
                "   border-radius: 20px;"  # העגולות תלמית כאן
                "   border: 2px solid #d0d0d0;"  # צבע המסגרת
                "}"
                "QPushButton:hover {"
                "   border: 2px solid #808080;"  # צבע המסגרת בעת העכבר מעל הכפתור
                "}"
                "QPushButton:hover:pressed {"
                "   border: 2px solid #4a4a4a;"  # צבע המסגרת בעת העכבר מעל הכפתור
                "}"
            )

        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.setWindowTitle("SettingsWindow")
        self.setGeometry(550, 400, 827, 208)


    def open_edit_dialog(self, book_data):
        self.close()
        dialog = EditBookDialog(book_data)
        dialog.exec_()

    def lend_or_return_book(self, book_data):
        self.close()

        data = read_archive_json()
        # לולאה עבור כל ספר ברשימת הספרים
        for book in data['books']:
            # בדוק אם ה"book_id" של הספר הוא 10000
            if book['book_id'] == book_data[0]:
                if book['is_borrowed'] == "לא":
                    # טען את תוכן הקובץ JSON
                    dialog5 = Borrower_detailsDialog()
                    dialog5.exec_()
                    if dialog5.ok_clicked:
                        book['is_borrowed'] = "כן"
                        dialog5.role = " (" + dialog5.role + ")"
                        if dialog5.role == " (ללא)":
                            dialog5.role = ""
                        book['borrower_name'] = dialog5.first_name + " " + dialog5.last_name + dialog5.role
                        book['borrower_id'] = dialog5.borrower_id
                        book['remarks'] = dialog5.remarks
                        current_date = datetime.date.today()
                        formatted_date = current_date.strftime("%d/%m/%Y")
                        book['loaning_date'] = str(formatted_date)

                elif book['is_borrowed'] == "כן":
                    book['is_borrowed'] = "לא"
                    book['borrower_name'] = ""
                    book['borrower_id'] = ""
                    book['remarks'] = ""
                    book['loaning_date'] = ""

                        # עדכן את המידע בקובץ JSON
            with open('dependence/ArcFiles/archive.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)


    def delete_this_book(self, book_data):
        self.close()
        # השתמש בפונקציה כדי למחוק ספר לפי ה-ID שלו
        id = [book_data[0]]
        delete_book_by_id(id)
        self.close()


class are_you_sure_window(QDialog):
    def __init__(self, books_ids):
        super().__init__()
        self.initUI(books_ids)

    def initUI(self, books_ids):
        self.data = False
        List_of_books_awaiting_deletion_approval = []
        self.setWindowTitle('עשרת השמות')
        self.setGeometry(550, 400, 700, 300)

        layout = QVBoxLayout(self)

        # הוספת המלל
        label = QLabel("האם אתה בטוח שברצונך להסיר את הספרים הבאים מן הארכיון:")
        layout.addWidget(label)

        # הוספת תיבת גלילה
        scroll_area = QScrollArea()
        layout.addWidget(scroll_area)

        # תיבת טקסט לתוך תיבת הגלילה
        text_widget = QWidget()
        scroll_area.setWidget(text_widget)

        text_layout = QVBoxLayout(text_widget)

        all_books = read_archive_json()

        for book in all_books["books"]:
            for id in books_ids:
                if book['book_id'] == id:
                    Book_details = (book['book_id'] + ", " + book['book_title'] + ", " + book['book_type'] + ", " + book['grade']
                         + ", " + book['age_group'] + ", " + book['author'] + ", " + book['publisher']
                         + ", " + book['series_name'] + ", " + book['series_part'] + ", " + book['shelf']
                         + ", " + book['amount_in_archive'] + ", " + book['book_condition']
                         + ", " + book['remarks'] + ", ")
                    List_of_books_awaiting_deletion_approval.append(Book_details)

        # הוספת השמות לתיבת הטקסט
        for name in List_of_books_awaiting_deletion_approval:
            name_label = QLabel(name)
            name_label.setAlignment(QtCore.Qt.AlignTop)
            text_layout.insertWidget(1, name_label)


        text_widget.setLayout(text_layout)
        scroll_area.setWidgetResizable(True)

        # שורת כפתורים
        buttons_layout = QHBoxLayout()

        # הוספת כפתור "כן"
        yes_button = QPushButton("כן", self)
        yes_button.clicked.connect(self.on_yes_click)

        # הוספת כפתור "לא"
        no_button = QPushButton("לא", self)
        no_button.clicked.connect(self.on_no_click)

        # הוספת הכפתורים לפריסת הכפתורים
        buttons_layout.addWidget(yes_button)
        buttons_layout.addWidget(no_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def on_yes_click(self):
        self.data = True
        self.accept()

    def on_no_click(self):
        self.data = False
        self.accept()


class Borrower_detailsDialog(QDialog):
    def __init__(self, ):
        super().__init__()

        self.setupUi()

    def setupUi(self):
        self.ok_clicked = False
        self.setWindowTitle('עשרת השמות')
        self.setGeometry(700, 400, 400, 300)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        self.main_frame = QtWidgets.QFrame(self)
        self.main_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.main_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_frame.setObjectName("main_frame")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.main_frame)
        self.verticalLayout.setObjectName("verticalLayout")

        # Borrower details frame
        self.Borrower_details_frame = QtWidgets.QFrame(self.main_frame)
        self.Borrower_details_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Borrower_details_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Borrower_details_frame.setObjectName("Borrower_details_frame")

        self.formLayout = QtWidgets.QFormLayout(self.Borrower_details_frame)
        self.formLayout.setObjectName("formLayout")

        self.Borrower_details_label = QtWidgets.QLabel(self.Borrower_details_frame)
        self.Borrower_details_label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.Borrower_details_label.setText("פרטי השואל (חובה):")
        self.Borrower_details_label.setObjectName("Borrower_details_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.Borrower_details_label)

        # first name
        self.first_name_lineEdit = QtWidgets.QLineEdit(self.Borrower_details_frame)
        self.first_name_lineEdit.setObjectName("first_name_lineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.first_name_lineEdit)
        self.first_name_label = QtWidgets.QLabel(self.Borrower_details_frame)
        self.first_name_label.setObjectName("first_name_label")
        self.first_name_label.setText("שם פרטי:")
        self.first_name_label.setStyleSheet("color: red;")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.first_name_label)

        # last name
        self.last_name_lineEdit = QtWidgets.QLineEdit(self.Borrower_details_frame)
        self.last_name_lineEdit.setObjectName("last_name_lineEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.last_name_lineEdit)
        self.last_name_label = QtWidgets.QLabel(self.Borrower_details_frame)
        self.last_name_label.setText("שם משפחה:")
        self.last_name_label.setStyleSheet("color: red;")
        self.last_name_label.setObjectName("last_name_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.last_name_label)

        # id
        self.id_lineEdit = QtWidgets.QLineEdit(self.Borrower_details_frame)
        self.id_lineEdit.setObjectName("id_lineEdit")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.id_lineEdit)
        self.id_label = QtWidgets.QLabel(self.Borrower_details_frame)
        self.id_label.setStyleSheet("color: red;")
        self.id_label.setText("תעודת זהות (מומלץ):")
        self.id_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.id_label.setObjectName("id_label")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.id_label)

        # role
        self.role_comboBox = QtWidgets.QComboBox(self.Borrower_details_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.role_comboBox.sizePolicy().hasHeightForWidth())
        self.role_comboBox.setSizePolicy(sizePolicy)
        self.role_comboBox.setMinimumSize(QtCore.QSize(0, 0))
        self.role_comboBox.setSizeIncrement(QtCore.QSize(0, 0))
        self.role_comboBox.setBaseSize(QtCore.QSize(0, 0))
        self.role_comboBox.setIconSize(QtCore.QSize(17, 17))
        self.role_comboBox.setObjectName("role_comboBox")
        self.role_comboBox.addItem("תלמיד")
        self.role_comboBox.addItem("מחנך/ת")
        self.role_comboBox.addItem("מורה")
        self.role_comboBox.addItem("הנהלה")
        self.role_comboBox.addItem("ללא")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.role_comboBox)

        self.role_label = QtWidgets.QLabel(self.Borrower_details_frame)
        self.role_label.setStyleSheet("color: red;")
        self.role_label.setText("תפקיד (מומלץ):")
        self.role_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.role_label.setObjectName("role_label")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.role_label)

        self.verticalLayout.addWidget(self.Borrower_details_frame)

        # remarks
        self.remarks_frame = QtWidgets.QFrame(self.main_frame)
        self.remarks_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.remarks_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.remarks_frame.setObjectName("remarks_frame")

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.remarks_frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.remarks_label = QtWidgets.QLabel(self.remarks_frame)
        self.remarks_label.setTextFormat(QtCore.Qt.AutoText)
        self.remarks_label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.remarks_label.setText("הערות (אופציונלי):")
        self.remarks_label.setObjectName("remarks_label")

        self.verticalLayout_3.addWidget(self.remarks_label)

        self.remarks_lineEdit = QtWidgets.QLineEdit(self.remarks_frame)
        self.remarks_lineEdit.setObjectName("remarks_lineEdit")

        self.verticalLayout_3.addWidget(self.remarks_lineEdit)
        self.verticalLayout.addWidget(self.remarks_frame)

        self.gridLayout.addWidget(self.main_frame, 0, 0, 1, 1)

        self.OK_and_Cancel_buttonBox = QtWidgets.QDialogButtonBox(self)
        self.OK_and_Cancel_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.OK_and_Cancel_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.OK_and_Cancel_buttonBox.setObjectName("OK_and_Cancel_buttonBox")

        self.gridLayout.addWidget(self.OK_and_Cancel_buttonBox, 1, 0, 1, 1)

        # הוסף לחיצה על כפתור "OK" לפונקציה שתטפל בלחיצה
        self.OK_and_Cancel_buttonBox.accepted.connect(self.on_ok_clicked)

        # הוסף לחיצה על כפתור "Cancel" לפונקציה שתטפל בלחיצה
        self.OK_and_Cancel_buttonBox.rejected.connect(self.on_cancel_clicked)

    def on_ok_clicked(self):

        if (
                self.first_name_lineEdit.text() == ""
                or self.last_name_lineEdit.text() == ""
        ):
            return

        self.role = self.role_comboBox.currentText()
        self.first_name = self.first_name_lineEdit.text().strip()
        self.last_name = self.last_name_lineEdit.text().strip()
        self.borrower_id = self.id_lineEdit.text().strip()
        self.remarks = self.remarks_lineEdit.text().strip()
        self.ok_clicked = True
        # סגור את החלון עם פרמטר בוליאני True (המציין שהלחיצה הייתה "OK")
        self.accept()

    def on_cancel_clicked(self):
        # סגור את החלון עם פרמטר בוליאני False (המציין שהלחיצה הייתה "Cancel" או הסגרת החלון)
        self.reject()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    icon = QIcon("dependence\images\Software icon.png")  # החלף את "path_to_your_icon_file.png" בנתיב לקובץ האיקון שלך
    window.setWindowIcon(icon)
    # הצגת החלון במסך מלא
    window.showMaximized()

    sys.exit(app.exec_())
