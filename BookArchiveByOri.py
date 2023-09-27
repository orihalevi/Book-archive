import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QAction, QToolBar, QVBoxLayout, QWidget, QLabel,
                             QScrollArea, QLineEdit, QHBoxLayout, QStatusBar, QDialog, QGroupBox, QGridLayout,
                             QShortcut, QComboBox, QPushButton, QFrame, QSplitter, QCheckBox, QDialogButtonBox, QSizePolicy)
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon, QKeySequence, QIntValidator, QPixmap, QFont
import os
import random
import json
import datetime

def read_archive_json():
    archive_path = "dependence/ArcFiles/archive.json"
    with open(archive_path, "r", encoding="utf-8") as file:
        all_books_data = json.load(file)
        return all_books_data

def books_in_archive():
    archive_file_content = read_archive_json()
    books_in_archive = archive_file_content["books"]
    return books_in_archive

def get_number_of_books_in_archive():
    books_data = books_in_archive()
    return len(books_data)



def write_update_to_the_archive_json(file_update):
    archive_path = "dependence/ArcFiles/archive.json"
    with open(archive_path, "w", encoding="utf-8") as file:
        json.dump(file_update, file, ensure_ascii=False, indent=4)

# Function to delete a book by its ID
def delete_book_by_id(books_ids):
    dialog3 = Are_you_sure_window(books_ids)
    dialog3.exec_()

    if dialog3.sure_to_delete:
        archive_file_content = read_archive_json()
        for id in books_ids:
            # מצא את הספר ברשימת הספרים לפי ה-ID
            for book in archive_file_content["books"]:
                if id == book['book_id']:
                    # Delete the book from the list
                    archive_file_content["books"].remove(book)

            # Save the information back to a JSON file
            write_update_to_the_archive_json(archive_file_content)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.general_widget_scrollArea = None
        self.groupBoxes_to_clear = []
        self.books_details_groupBoxes = []

        self.limit_books_display_amount = True
        self.limit_books_display = 50

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

        self.setWindowTitle("ארכיון ספרים - בית יהודה")
        self.setGeometry(100, 100, 1500, 900)

        # Creating status bar object
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        # Setting text in status bar
        self.status_bar.showMessage("סטטוס: מוכן")

        self.MainWindow_layout = None

        self.initui()

    def initui(self):
        # Creating a widget that surrounds all the GUI components that will be in the window
        # It's like a frame but invisible
        MainWindow_central_widget = QWidget(self)
        self.setCentralWidget(MainWindow_central_widget)

        # Creating the main layout/tunnel/תַסדִיר according to which all components will be arranged
        # In this case, they will be: groupBox ("מנוע חיפוש"), books_displaying_scrollArea
        self.MainWindow_layout = QVBoxLayout(MainWindow_central_widget)

        self.create_bars()
        self.create_search_engine_graphical_interface()
        self.creating_a_frame_with_a_scroll_bar()
        self.load_archive()

    def create_bars(self):
        # create a menu bar
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("קובץ")

        open_folder_action = QAction("בחר מתיקייה", self)
        #open_folder_action.triggered.connect(self.open_file)
        file_menu.addAction(open_folder_action)

        exit_action = QAction("יציאה", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menu_bar.addMenu("כלים")
        Manage_json_files_action = QAction("נהל קבצי json", self)
        #Manage_json_files_action.triggered.connect(self.manage_json_files)
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


    def create_search_engine_graphical_interface(self):
        # Create groupBox for the search engine
        search_engine_groupBox = QGroupBox("מנוע חיפוש", self)
        search_engine_groupBox.setAlignment(QtCore.Qt.AlignRight)   # Aline title to the right
        # Add the components to MainWindow_layout
        self.MainWindow_layout.addWidget(search_engine_groupBox)

        # Create a grid layout to gut the components inside
        search_groupBox_grid_layout = QGridLayout(search_engine_groupBox)

        # Create the top frame for the top search boxes line
        top_frame_in_search_groupBox = QWidget(search_engine_groupBox)
        search_groupBox_grid_layout.addWidget(top_frame_in_search_groupBox, 0, 1)

        # Organize the components inside the top_frame_in_search_groupBox in grid order
        top_frame_grid_layout = QGridLayout(top_frame_in_search_groupBox)

        # book id field
        self.line_edit_book_id = QLineEdit(top_frame_in_search_groupBox)
        self.line_edit_book_id.textChanged.connect(self.load_archive)
        self.line_edit_book_id.setObjectName("lineEdit")
        self.line_edit_book_id.setPlaceholderText("הזן מזהה הספר")
        top_frame_grid_layout.addWidget(self.line_edit_book_id, 1, 7, 1, 1)

        # book neme field
        self.line_edit_book_title = QLineEdit(top_frame_in_search_groupBox)
        self.line_edit_book_title.textChanged.connect(self.load_archive)
        self.line_edit_book_title.setObjectName("lineEdit")
        self.line_edit_book_title.setPlaceholderText("הזן שם הספר")
        top_frame_grid_layout.addWidget(self.line_edit_book_title, 1, 6, 1, 1)

        # series name field
        self.line_edit_series_name = QLineEdit(top_frame_in_search_groupBox)
        self.line_edit_series_name.textChanged.connect(self.load_archive)
        self.line_edit_series_name.setObjectName("lineEdit_2")
        self.line_edit_series_name.setPlaceholderText("הזן שם הסדרה")
        top_frame_grid_layout.addWidget(self.line_edit_series_name, 1, 5, 1, 1)

        # series part field
        self.line_edit_series_part = QLineEdit(top_frame_in_search_groupBox)
        self.line_edit_series_part.textChanged.connect(self.load_archive)
        self.line_edit_series_part.setObjectName("lineEdit_12")
        self.line_edit_series_part.setPlaceholderText("הזן חלק בסדרה")
        top_frame_grid_layout.addWidget(self.line_edit_series_part, 1, 4, 1, 1)

        # grade field
        self.line_edit_grade = QLineEdit(top_frame_in_search_groupBox)
        self.line_edit_grade.textChanged.connect(self.load_archive)
        self.line_edit_grade.setObjectName("lineEdit_grade")
        self.line_edit_grade.setPlaceholderText("הזן כיתה")
        top_frame_grid_layout.addWidget(self.line_edit_grade, 1, 3, 1, 1)

        # age group field
        self.line_edit_age_group = QLineEdit(top_frame_in_search_groupBox)
        self.line_edit_age_group.textChanged.connect(self.load_archive)
        self.line_edit_age_group.setObjectName("lineEdit_age_group")
        self.line_edit_age_group.setPlaceholderText("הזן שכבת גיל")
        top_frame_grid_layout.addWidget(self.line_edit_age_group, 1, 2, 1, 1)

        # author field
        self.line_edit_author = QLineEdit(top_frame_in_search_groupBox)
        self.line_edit_author.textChanged.connect(self.load_archive)
        self.line_edit_author.setObjectName("lineEdit_author")
        self.line_edit_author.setPlaceholderText("הזן מחבר")
        top_frame_grid_layout.addWidget(self.line_edit_author, 1, 1, 1, 1)

        # Publisher field
        self.line_edit_publisher = QLineEdit(top_frame_in_search_groupBox)
        self.line_edit_publisher.textChanged.connect(self.load_archive)
        self.line_edit_publisher.setObjectName("lineEdit_author")
        self.line_edit_publisher.setPlaceholderText("הזן מוציא לאור")
        top_frame_grid_layout.addWidget(self.line_edit_publisher, 1, 0, 1, 1)

        # Create the lower frame for the lower search boxes line
        lower_frame_in_search_groupBox = QWidget(search_engine_groupBox)
        search_groupBox_grid_layout.addWidget(lower_frame_in_search_groupBox, 1, 1)

        # Organize the components inside the lower_frame_in_search_groupBox in grid order
        lower_frame_grid_layout = QGridLayout(lower_frame_in_search_groupBox)

        # Shelf field
        self.line_edit_shelf = QLineEdit(lower_frame_in_search_groupBox)
        self.line_edit_shelf.textChanged.connect(self.load_archive)
        self.line_edit_shelf.setObjectName("lineEdit_11")
        self.line_edit_shelf.setPlaceholderText("הזן מדף")
        lower_frame_grid_layout.addWidget(self.line_edit_shelf, 1, 8, 1, 1)

        # Amount in archive field
        self.line_edit_amount_in_archive = QLineEdit(lower_frame_in_search_groupBox)
        self.line_edit_amount_in_archive.textChanged.connect(self.load_archive)
        self.line_edit_amount_in_archive.setObjectName("lineEdit_13")
        self.line_edit_amount_in_archive.setPlaceholderText("הזן כמות בארכיון")
        lower_frame_grid_layout.addWidget(self.line_edit_amount_in_archive, 1, 7, 1, 1)

        # is borrowed field
        self.is_borrowed_combo_box = QComboBox(lower_frame_in_search_groupBox)
        self.is_borrowed_combo_box.addItem("האם מושאל")
        self.is_borrowed_combo_box.addItem("כן")
        self.is_borrowed_combo_box.addItem("לא")
        self.is_borrowed_combo_box.currentIndexChanged.connect(self.load_archive)
        self.is_borrowed_combo_box.setPlaceholderText("האם מושאל")
        lower_frame_grid_layout.addWidget(self.is_borrowed_combo_box, 1, 6, 1, 1)

        # book condition field
        self.book_condition_combo_box = QComboBox(lower_frame_in_search_groupBox)
        self.book_condition_combo_box.addItem("בחר מצב ספר")
        self.book_condition_combo_box.addItem("חדש")
        self.book_condition_combo_box.addItem("משומש")
        self.book_condition_combo_box.addItem("פתור/כתוב")
        self.book_condition_combo_box.addItem("קרוע")
        self.book_condition_combo_box.addItem("לא ידוע")
        self.book_condition_combo_box.currentIndexChanged.connect(self.load_archive)
        self.book_condition_combo_box.setObjectName("fontComboBox_2")
        self.book_condition_combo_box.setPlaceholderText("בחר מצב ספר")
        lower_frame_grid_layout.addWidget(self.book_condition_combo_box, 1, 5, 1, 1)

        # loaning date filed
        self.line_edit_loaning_date = QLineEdit(lower_frame_in_search_groupBox)
        self.line_edit_loaning_date.textChanged.connect(self.load_archive)
        self.line_edit_loaning_date.setObjectName("lineEdit_9")
        self.line_edit_loaning_date.setPlaceholderText("הזן תאריך השאלה")
        lower_frame_grid_layout.addWidget(self.line_edit_loaning_date, 1, 4, 1, 1)

        # book type field
        self.book_type_combo_box = QComboBox(lower_frame_in_search_groupBox)
        self.book_type_combo_box.addItem("בחר סוג ספר")
        self.book_type_combo_box.addItem("קודש")
        self.book_type_combo_box.addItem("כתיבה")
        self.book_type_combo_box.addItem("קריאה")
        self.book_type_combo_box.addItem("לימוד")
        self.book_type_combo_box.addItem("אחר")
        self.book_type_combo_box.currentIndexChanged.connect(self.load_archive)
        self.book_type_combo_box.setObjectName("fontComboBox")
        self.book_type_combo_box.setPlaceholderText("בחר סוג ספר")
        lower_frame_grid_layout.addWidget(self.book_type_combo_box, 1, 3, 1, 1)

        # borrower name field
        self.line_edit_borrower_name = QLineEdit(lower_frame_in_search_groupBox)
        self.line_edit_borrower_name.textChanged.connect(self.load_archive)
        self.line_edit_borrower_name.setObjectName("lineEdit_10")
        self.line_edit_borrower_name.setPlaceholderText("הזן שם השואל/הלוקח")
        lower_frame_grid_layout.addWidget(self.line_edit_borrower_name, 1, 2, 1, 1)

        # borrower id field
        self.line_edit_borrower_id = QLineEdit(lower_frame_in_search_groupBox)
        self.line_edit_borrower_id.textChanged.connect(self.load_archive)
        self.line_edit_borrower_id.setObjectName("lineEdit_4")
        self.line_edit_borrower_id.setPlaceholderText("הזן תעודת זהות השואל")
        lower_frame_grid_layout.addWidget(self.line_edit_borrower_id, 1, 1, 1, 1)

        # remarks field
        self.line_edit_remarks = QLineEdit(lower_frame_in_search_groupBox)
        self.line_edit_remarks.textChanged.connect(self.load_archive)
        self.line_edit_remarks.setObjectName("lineEdit_4")
        self.line_edit_remarks.setPlaceholderText("הזן הערות (אם יש)")
        lower_frame_grid_layout.addWidget(self.line_edit_remarks, 1, 0, 1, 1)

    def creating_a_frame_with_a_scroll_bar(self):
        # Creating a ScrollArea with a scroll bar for displaying the books details
        self.books_displaying_scrollArea = QtWidgets.QScrollArea(self)
        self.books_displaying_scrollArea.setWidgetResizable(True)
        # add the scrollarea to the MainWindow_layout
        self.MainWindow_layout.addWidget(self.books_displaying_scrollArea)

        # Creating a widget that surrounds all the GUI components that will be in the books_displaying_scrollArea
        # It's like a frame but invisible
        self.general_widget_scrollArea = QWidget()
        self.general_widget_scrollArea.setGeometry(QtCore.QRect(0, 0, 1539, 507))
        self.general_widget_scrollArea.setObjectName("general_widget_scrollArea")

        # Inserts general_widget_scrollArea into books_displaying_scrollArea and thus sets the scrolling
        self.books_displaying_scrollArea.setWidget(self.general_widget_scrollArea)

        # Create first splitter to attach the books_details_groupBoxes to the corners of general_widget_scrollArea
        self.Main_splitter = QSplitter(self.general_widget_scrollArea)
        self.Main_splitter.setOrientation(QtCore.Qt.Horizontal)

        # Organize the components inside the general_widget_scrollArea in grid order
        self.general_widget_gridLayout = QGridLayout(self.general_widget_scrollArea)
        self.general_widget_gridLayout.addWidget(self.Main_splitter, 0, 0, 1, 1)



        # צריך לסדר
        self.Reveal_all_books_button_widget = QWidget(self.general_widget_scrollArea)
        self.Reveal_all_books_button_widget.setObjectName("widget")
        self.verticalLayout = QVBoxLayout(self.Reveal_all_books_button_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Reveal_all_books_button = QPushButton(self.Reveal_all_books_button_widget)
        self.Reveal_all_books_button.setText("הצג כל את הספרים")
        self.Reveal_all_books_button.setObjectName("Reveal_all_books_button")
        self.Reveal_all_books_button.clicked.connect(self.toggle_limit_books_display)
        self.verticalLayout.addWidget(self.Reveal_all_books_button)
        self.general_widget_gridLayout.addWidget(self.Reveal_all_books_button_widget, 1, 0, 1, 1)

        self.no_books_to_dislpay_label = QLabel("אין ספרים להצגה", self.Reveal_all_books_button_widget)
        # הגדרת פונט מודגש וגדול
        self.font = QFont()
        self.font.setBold(True)
        self.font.setPointSize(70)
        self.verticalLayout.addWidget(self.no_books_to_dislpay_label)


        # Create the second splitter to split between every group box
        self.groupBoxes_splitter = QSplitter(self.Main_splitter)
        self.groupBoxes_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.groupBoxes_splitter.setOpaqueResize(True)
        self.groupBoxes_splitter.setChildrenCollapsible(False)
        # Create group boxes and insert them into the splitter:
        # remarks
        self.remarks_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.remarks_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.remarks_groupBox.setFlat(True)
        self.remarks_groupBox.setTitle("הערות")
        self.books_details_groupBoxes.append(self.remarks_groupBox)

        self.remarks_groupBox_gridLayout = QGridLayout(self.remarks_groupBox)
        self.remarks_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.remarks_groupBox_gridLayout)

        # borrower id
        self.borrower_id_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.borrower_id_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.borrower_id_groupBox.setFlat(True)
        self.borrower_id_groupBox.setTitle("תעודת זהות")
        self.books_details_groupBoxes.append(self.borrower_id_groupBox)

        self.borrower_id_groupBox_gridLayout = QGridLayout(self.borrower_id_groupBox)
        self.borrower_id_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.borrower_id_groupBox_gridLayout)

        # borrower name
        self.borrower_name_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.borrower_name_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.borrower_name_groupBox.setFlat(True)
        self.borrower_name_groupBox.setTitle("שם השואל/הלוקח")
        self.books_details_groupBoxes.append(self.borrower_name_groupBox)

        self.borrower_name_groupBox_gridLayout = QGridLayout(self.borrower_name_groupBox)
        self.borrower_name_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.borrower_name_groupBox_gridLayout)

        # book type
        self.book_type_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.book_type_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.book_type_groupBox.setFlat(True)
        self.book_type_groupBox.setTitle("סוג הספר")
        self.books_details_groupBoxes.append(self.book_type_groupBox)

        self.book_type_groupBox_gridLayout = QGridLayout(self.book_type_groupBox)
        self.book_type_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.book_type_groupBox_gridLayout)

        # loaning date
        self.loaning_date_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.loaning_date_groupBox.setEnabled(True)
        self.loaning_date_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.loaning_date_groupBox.setFlat(True)
        self.loaning_date_groupBox.setTitle("תאריך השאלה")
        self.books_details_groupBoxes.append(self.loaning_date_groupBox)

        self.loaning_date_groupBox_gridLayout = QGridLayout(self.loaning_date_groupBox)
        self.loaning_date_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.loaning_date_groupBox_gridLayout)

        # book condition
        self.book_condition_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.book_condition_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.book_condition_groupBox.setFlat(True)
        self.book_condition_groupBox.setTitle("מצב הספר")
        self.books_details_groupBoxes.append(self.book_condition_groupBox)

        self.book_condition_groupBox_gridLayout = QGridLayout(self.book_condition_groupBox)
        self.book_condition_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.book_condition_groupBox_gridLayout)

        # is borrowed
        self.is_borrowed_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.is_borrowed_groupBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.is_borrowed_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.is_borrowed_groupBox.setFlat(True)
        self.is_borrowed_groupBox.setTitle("מושאל")
        self.books_details_groupBoxes.append(self.is_borrowed_groupBox)

        self.is_borrowed_groupBox_gridLayout = QGridLayout(self.is_borrowed_groupBox)
        self.is_borrowed_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.is_borrowed_groupBox_gridLayout)

        # amount in archive
        self.amount_in_archive_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.amount_in_archive_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.amount_in_archive_groupBox.setFlat(True)
        self.amount_in_archive_groupBox.setTitle("כמות בארכיון")
        self.books_details_groupBoxes.append(self.amount_in_archive_groupBox)

        self.amount_in_archive_groupBox_gridLayout = QGridLayout(self.amount_in_archive_groupBox)
        self.amount_in_archive_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.amount_in_archive_groupBox_gridLayout)

        # shelf
        self.shelf_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.shelf_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.shelf_groupBox.setFlat(True)
        self.shelf_groupBox.setTitle("מדף")
        self.books_details_groupBoxes.append(self.shelf_groupBox)

        self.shelf_groupBox_gridLayout = QGridLayout(self.shelf_groupBox)
        self.shelf_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.shelf_groupBox_gridLayout)

        # publisher
        self.publisher_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.publisher_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.publisher_groupBox.setFlat(True)
        self.publisher_groupBox.setTitle("מוציא לאור")
        self.books_details_groupBoxes.append(self.publisher_groupBox)

        self.publisher_groupBox_gridLayout = QGridLayout(self.publisher_groupBox)
        self.publisher_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.publisher_groupBox_gridLayout)

        # author
        self.author_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.author_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.author_groupBox.setFlat(True)
        self.author_groupBox.setTitle("מחבר")
        self.books_details_groupBoxes.append(self.author_groupBox)

        self.author_groupBox_gridLayout = QGridLayout(self.author_groupBox)
        self.author_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.author_groupBox_gridLayout)

        # age group
        self.age_group_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.age_group_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.age_group_groupBox.setFlat(True)
        self.age_group_groupBox.setTitle("שכבת גיל")
        self.books_details_groupBoxes.append(self.age_group_groupBox)

        self.age_group_groupBox_gridLayout = QGridLayout(self.age_group_groupBox)
        self.age_group_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.age_group_groupBox_gridLayout)

        # grade
        self.grade_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.grade_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.grade_groupBox.setFlat(True)
        self.grade_groupBox.setTitle("כיתה")
        self.books_details_groupBoxes.append(self.grade_groupBox)

        self.grade_groupBox_gridLayout = QGridLayout(self.grade_groupBox)
        self.grade_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.grade_groupBox_gridLayout)

        # series part
        self.series_part_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.series_part_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.series_part_groupBox.setFlat(True)
        self.series_part_groupBox.setTitle("חלק בסדרה")
        self.books_details_groupBoxes.append(self.series_part_groupBox)

        self.series_part_groupBox_gridLayout = QGridLayout(self.series_part_groupBox)
        self.series_part_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.series_part_groupBox_gridLayout)

        # series name
        self.series_name_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.series_name_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.series_name_groupBox.setFlat(True)
        self.series_name_groupBox.setTitle("שם הסדרה")
        self.books_details_groupBoxes.append(self.series_name_groupBox)

        self.series_name_groupBox_gridLayout = QGridLayout(self.series_name_groupBox)
        self.series_name_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.series_name_groupBox_gridLayout)

        # book name
        self.book_name_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.book_name_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.book_name_groupBox.setFlat(True)
        self.book_name_groupBox.setTitle("שם הספר")
        self.books_details_groupBoxes.append(self.book_name_groupBox)

        self.book_name_groupBox_gridLayout = QGridLayout(self.book_name_groupBox)
        self.book_name_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.book_name_groupBox_gridLayout)

        # book_id
        self.book_id_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.book_id_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.book_id_groupBox.setFlat(True)
        self.book_id_groupBox.setTitle("מזהה")
        self.books_details_groupBoxes.append(self.book_id_groupBox)

        self.book_id_groupBox_gridLayout = QGridLayout(self.book_id_groupBox)
        self.book_id_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.book_id_groupBox_gridLayout)

        # tools
        self.tools_groupBox = QtWidgets.QGroupBox(self.groupBoxes_splitter)
        self.tools_groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.tools_groupBox.setFlat(True)
        self.tools_groupBox.setTitle("כלים")
        self.tools_groupBox.setObjectName("tools_groupBox")
        self.books_details_groupBoxes.append(self.tools_groupBox)

        self.tools_groupBox_gridLayout = QGridLayout(self.tools_groupBox)
        self.tools_groupBox_gridLayout.setContentsMargins(0, -1, 0, -1)
        self.groupBoxes_to_clear.append(self.tools_groupBox_gridLayout)

    def toggle_limit_books_display(self):
        self.limit_books_display_amount = False
        self.load_archive()
        self.limit_books_display_amount = True


    def load_archive(self):
        self.clear_books_details_groupBoxes()
        self.calculate_each_book_amount_in_the_archive()
        # Reset the amount of books displayed
        Rows_of_books_entered_the_display = 0
        for book in books_in_archive():
            # A condition that compares the content written in the search to the details of the books
            if (
                    (self.line_edit_book_id.text() == "" or self.line_edit_book_id.text() in book["book_id"]) and
                    (self.line_edit_book_title.text() == "" or self.line_edit_book_title.text() in book["book_title"]) and
                    (self.book_type_combo_box.currentText() == "בחר סוג ספר" or self.book_type_combo_box.currentText() in book["book_type"]) and
                    (self.line_edit_author.text() == "" or self.line_edit_author.text() in book["author"]) and
                    (self.line_edit_publisher.text() == "" or self.line_edit_publisher.text() in book["publisher"]) and
                    (self.line_edit_series_name.text() == "" or self.line_edit_series_name.text() in book["series_name"]) and
                    (self.line_edit_series_part.text() == "" or self.line_edit_series_part.text() in book["series_part"]) and
                    (self.line_edit_grade.text() == "" or self.line_edit_grade.text() in book["grade"]) and
                    (self.line_edit_age_group.text() == "" or self.line_edit_age_group.text() in book["age_group"]) and
                    (self.is_borrowed_combo_box.currentText() == "האם מושאל" or self.is_borrowed_combo_box.currentText() in book["is_borrowed"]) and
                    (self.line_edit_borrower_name.text() == "" or self.line_edit_borrower_name.text() in book["borrower_name"]) and
                    (self.line_edit_loaning_date.text() == "" or self.line_edit_loaning_date.text() in book["loaning_date"]) and
                    (self.line_edit_shelf.text() == "" or self.line_edit_shelf.text() in book["shelf"]) and
                    (self.line_edit_amount_in_archive.text() == "" or self.line_edit_amount_in_archive.text() in book["amount_in_archive"]) and
                    (self.book_condition_combo_box.currentText() == "בחר מצב ספר" or self.book_condition_combo_box.currentText() in book["book_condition"]) and
                    (self.line_edit_borrower_id.text() == "" or self.line_edit_borrower_id.text() in book["borrower_id"]) and
                    (self.line_edit_remarks.text() == "" or self.line_edit_remarks.text() in book["remarks"])
            ):

                # empty dictionary
                book_data = {}
                # Adding the book details to the dictionary
                book_data["remarks"] = book["remarks"]
                book_data["borrower_id"] = book["borrower_id"]
                book_data["borrower_name"] = book["borrower_name"]
                book_data["book_type"] = book["book_type"]
                book_data["loaning_date"] = book["loaning_date"]
                book_data["book_condition"] = book["book_condition"]
                book_data["is_borrowed"] = book["is_borrowed"]
                book_data["amount_in_archive"] = book["amount_in_archive"]
                book_data["shelf"] = book["shelf"]
                book_data["publisher"] = book["publisher"]
                book_data["author"] = book["author"]
                book_data["age_group"] = book["age_group"]
                book_data["grade"] = book["grade"]
                book_data["series_part"] = book["series_part"]
                book_data["series_name"] = book["series_name"]
                book_data["book_title"] = book["book_title"]
                book_data["book_id"] = book["book_id"]

                # A loop that goes through every detail in the dictionary and puts it inside QLineEdit
                for key, value in enumerate(book_data):
                    edit_line = QLineEdit(book_data[value], self)
                    edit_line.setReadOnly(True)
                    edit_line.setToolTip(str(self.books_details_groupBoxes[key].title()) + ": " + str(book_data[value]))
                    self.books_details_groupBoxes[key].layout().addWidget(edit_line)
                    # A condition that changes the background color of is_borrowed if the book is borrowed
                    if value == "is_borrowed":
                        edit_line.setStyleSheet("background-color: #EF9A9A;")
                        if book_data[value] == "לא":
                            edit_line.setStyleSheet("background-color: #C5E1A5;")

                # Creating a book_setting button
                edit_button = QPushButton(QIcon(r'dependence\images\book_setting.png'), '')
                edit_button.setStyleSheet(
                    'background-color: transparent; border: 1px solid #d0d0d0; border-radius: 3px;')
                edit_button.setFixedSize(21, 21)
                edit_button.clicked.connect(lambda state, this_book_id=book["book_id"]: self.edit_book_data(this_book_id))
                for groupBox in self.books_details_groupBoxes:
                    if groupBox.objectName() == "tools_groupBox":
                        groupBox.layout().addWidget(edit_button)

                # Limit display to prevent delays, prat 1 (of 2)
                Rows_of_books_entered_the_display += 1

            # Limit display to prevent delays, prat 2 (of 2)
            if not self.limit_books_display_amount:
                # Don't show Reveal_all_books_button if limit_books_display_amount
                self.Reveal_all_books_button.close()
                # go back to the start in the loop
                continue

            # If we have reached the display limit then stop the loop and display the button Reveal_all_books_button
            if Rows_of_books_entered_the_display == self.limit_books_display:
                self.Reveal_all_books_button.show()
                break

        # Creating an empty label inside each groupBox to attach the lineedits
        for groupBox in self.books_details_groupBoxes:
            name_label = QLabel("")
            name_label.setAlignment(QtCore.Qt.AlignTop)
            groupBox.layout().addWidget(name_label)


        """
        # A loop that hides all the G from the display,
        # this loop is useful in the future for displaying the label "No books matching the search were found"
        for groupBox in self.books_details_groupBoxes:
            groupBox.setVisible(False)  # להסתיר את הרכיב
        """

    def clear_books_details_groupBoxes(self):
        for groupBox in self.books_details_groupBoxes:
            layout = groupBox.layout()
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

    #  A function that calculates the amount of each book in the archive by summing the values:
    #  "book_title, series_name, series_part, grade, age_group, author, and publisher"
    #  and then edits the amount_in_archive value in each book accordingly.
    def calculate_each_book_amount_in_the_archive(self):
        duplicate_book_IDs = []
        archive_file_content = read_archive_json()
        # A loop that goes through all the books
        for book in archive_file_content["books"]:
            if book["book_id"] not in duplicate_book_IDs:
                duplicate_book_IDs = []
                current_book_title = book["book_title"]
                current_series_name = book["series_name"]
                current_series_part = book["series_part"]
                current_grade = book["grade"]
                current_age_group = book["age_group"]
                current_author = book["author"]
                current_publisher = book["publisher"]
                # A loop that compares the details of the current book with the details of the other books
                for book in archive_file_content["books"]:
                    if (
                            current_book_title == book["book_title"]
                            and current_series_name == book["series_name"]
                            and current_series_part == book["series_part"]
                            and current_grade == book["grade"]
                            and current_age_group == book["age_group"]
                            and current_author == book["author"]
                            and current_publisher == book["publisher"]
                    ):
                        # A condition that inserts the found double book into an array
                        if book["book_id"] not in duplicate_book_IDs:
                            duplicate_book_IDs.append(book["book_id"])
                    else:
                        # If this book is not found to match the current book, go to compare the next book with the current book
                        continue

                # A loop that will go through the matching books and set their amount_in_archive value according to their amount
                for book in archive_file_content["books"]:
                    if book["book_id"] in duplicate_book_IDs:
                        book["amount_in_archive"] = str(len(duplicate_book_IDs))
                # After we have made the changes in the books, we will save the file again
                write_update_to_the_archive_json(archive_file_content)

    # A function to break down the book into details and then send the details to the settings window
    def edit_book_data(self, this_book_id):
        for book in books_in_archive():
            if book["book_id"] == this_book_id:
                book_data = {}
                # Adding the book details to the dictionary
                book_data["book_id"] = book["book_id"]
                book_data["book_title"] = book["book_title"]
                book_data["series_name"] = book["series_name"]
                book_data["series_part"] = book["series_part"]
                book_data["grade"] = book["grade"]
                book_data["age_group"] = book["age_group"]
                book_data["author"] = book["author"]
                book_data["publisher"] = book["publisher"]
                book_data["shelf"] = book["shelf"]
                book_data["amount_in_archive"] = book["amount_in_archive"]
                book_data["is_borrowed"] = book["is_borrowed"]
                book_data["book_condition"] = book["book_condition"]
                book_data["loaning_date"] = book["loaning_date"]
                book_data["book_type"] = book["book_type"]
                book_data["borrower_name"] = book["borrower_name"]
                book_data["borrower_id"] = book["borrower_id"]
                book_data["remarks"] = book["remarks"]

        self.open_book_settings_dialog(book_data)
        self.load_archive()

    # A function to open the dialog for editing the book details
    def open_book_settings_dialog(self, book_data):
        book_settings = book_settings_dialog(book_data)
        book_settings.exec_()

    # So far the songs are placed in the window and the software alerts you to anything that is needed
    # From here on, the buttons actions

    def add_books_action_triggered(self):
        Add_new_books = Add_new_books_dialog()
        Add_new_books.exec_()
        self.load_archive()

    def clear_action_triggered(self):
        pass

    def restore_names_triggered(self):
        pass

class book_settings_dialog(QDialog):
    def __init__(self, book_data):
        super().__init__()

        self.Creating_a_book_settings_dialog_GUI(book_data)

    def Creating_a_book_settings_dialog_GUI(self, book_data):
        self.this_original_book_id = book_data["book_id"]
        self.setWindowTitle(f"הגדרות ספר {self.this_original_book_id}")
        self.setFixedSize(827, 208)

        # Create main frame for all components
        self.book_settings_dialog_main_frame = QFrame(self)
        self.book_settings_dialog_main_frame.setFrameShape(QFrame.StyledPanel)
        #self.book_settings_dialog_main_frame.setFrameShape(QFrame.Panel)
        #self.book_settings_dialog_main_frame.setFrameShape(QFrame.Box)
        self.book_settings_dialog_main_frame.setFrameShadow(QFrame.Raised)

        # Organize the components inside the book_settings_dialog_main_frame in grid order
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.addWidget(self.book_settings_dialog_main_frame, 0, 0, 1, 1)

        # Create delete book button
        self.delete_book_button = QPushButton(self.book_settings_dialog_main_frame)
        self.delete_book_button.setGeometry(QtCore.QRect(20, 20, 150, 150))
        self.delete_book_button.clicked.connect(lambda: self.delete_this_book(book_data))
        self.delete_book_button_pixmap = QPixmap('dependence/images/delete_book.png')
        self.delete_book_button.setIconSize(self.delete_book_button.size())
        self.delete_book_button.setIcon(QIcon(self.delete_book_button_pixmap))

        # Create duplicate book button
        self.duplicate_book_button = QPushButton(self.book_settings_dialog_main_frame)
        self.duplicate_book_button.setGeometry(QtCore.QRect(225, 20, 150, 150))
        self.duplicate_book_button.clicked.connect(lambda: self.open_duplicate_book(book_data))
        self.duplicate_book_button_pixmap = QPixmap('dependence/images/add_book.png')
        self.duplicate_book_button.setIconSize(self.duplicate_book_button.size())
        self.duplicate_book_button.setIcon(QIcon(self.duplicate_book_button_pixmap))

        # Create Borrow book button
        self.Borrow_book_button = QPushButton(self.book_settings_dialog_main_frame)
        self.Borrow_book_button.setGeometry(QtCore.QRect(430, 20, 150, 150))
        self.Borrow_book_button.clicked.connect(lambda: self.lend_or_return_book(book_data))
        self.Borrow_book_button_pixmap = QPixmap('dependence/images/nook_return.png')
        self.Borrow_book_button.setIconSize(self.Borrow_book_button.size())
        self.Borrow_book_button.setIcon(QIcon(self.Borrow_book_button_pixmap))
        if book_data["is_borrowed"] == "לא":
            self.Borrow_book_button_pixmap = QPixmap('dependence/images/book_lend.png')
            self.Borrow_book_button.setIcon(QIcon(self.Borrow_book_button_pixmap))

        # Create edit book details button
        self.edit_book_details_button = QPushButton(self.book_settings_dialog_main_frame)
        self.edit_book_details_button.setGeometry(QtCore.QRect(635, 20, 150, 150))
        self.edit_book_details_button.clicked.connect(lambda: self.open_editing_book_details_dialog(book_data))
        self.edit_book_details_button_pixmap = QPixmap('dependence/images/edit_book.png')
        self.edit_book_details_button.setIconSize(self.edit_book_details_button.size())
        self.edit_book_details_button.setIcon(QIcon(self.edit_book_details_button_pixmap))

        SettingsButtons = [
            self.delete_book_button,
            self.duplicate_book_button,
            self.Borrow_book_button,
            self.edit_book_details_button
        ]

        for button in SettingsButtons:
            button.setStyleSheet(
                "QPushButton {"
                "   border-radius: 20px;"  # Rounding the button frame
                "   border: 2px solid #d0d0d0;"  # frame color
                "}"
                "QPushButton:hover {"
                "   border: 2px solid #808080;"  # The frame color when the mouse hovers over the button
                "}"
                "QPushButton:hover:pressed {"
                "   border: 2px solid #4a4a4a;"  # The frame color when the mouse clicks the button
                "}"
            )

    def open_editing_book_details_dialog(self, book_data):
        self.close()
        editing_book_details = editing_book_details_dialog(book_data)
        editing_book_details.exec_()

    def lend_or_return_book(self, book_data):
        self.close()

        archive_file_content = read_archive_json()
        # Loop over all books
        for book in archive_file_content['books']:
            # If the book is the current book
            if book['book_id'] == book_data["book_id"]:
                # If the value is_borrowed is negative
                if book['is_borrowed'] == "לא":
                    Borrower_details = self.open_Borrower_details_dialog(book_data["remarks"])
                    if Borrower_details.Book_loan_approval:
                        book['is_borrowed'] = "כן"
                        # add role the value borrower_name
                        Borrower_details.role = " (" + Borrower_details.role + ")"
                        if Borrower_details.role == " (ללא)":
                            Borrower_details.role = ""
                        book['borrower_name'] = Borrower_details.first_name + " " + Borrower_details.last_name + Borrower_details.role
                        # fill the value borrower_id
                        book['borrower_id'] = Borrower_details.borrower_id
                        # fill the value remarks
                        book['remarks'] = Borrower_details.remarks
                        # fill the value loaning_date
                        current_date = datetime.date.today()
                        formatted_date = current_date.strftime("%d/%m/%Y")
                        book['loaning_date'] = str(formatted_date)
                # If the value is_borrowed is positive
                elif book['is_borrowed'] == "כן":
                    Is_book_returned_yes_clicked, Is_book_returned_delete_remarks = self.open_Is_book_returned_dialog(book_data)
                    if Is_book_returned_yes_clicked:
                        book['is_borrowed'] = "לא"
                        book['borrower_name'] = ""
                        book['borrower_id'] = ""
                        book['loaning_date'] = ""
                        if Is_book_returned_delete_remarks:
                            book['remarks'] = ""

            # Update the information in the JSON file
            write_update_to_the_archive_json(archive_file_content)

    def open_Borrower_details_dialog(self, book_remarks):
        Borrower_details = Borrower_details_dialog(book_remarks)
        Borrower_details.exec_()
        return Borrower_details

    def open_Is_book_returned_dialog(self, book_data):
        yes_clicked = False
        delete_remarks = False
        Is_book_returned = Is_book_returned_dialog(book_data)
        if Is_book_returned.exec_() == QDialog.Accepted:
            yes_clicked = True
            if Is_book_returned.delete_remarks_check_box.isChecked():
                delete_remarks = True
        return yes_clicked, delete_remarks

    def delete_this_book(self, book_data):
        self.close()
        this_book_id = [book_data["book_id"]]
        # Use this function to delete a book by its id
        delete_book_by_id(this_book_id)

    def open_duplicate_book(self, book_data):
        self.close()
        Duplicate_book = Duplicate_book_Dialog(book_data)
        Duplicate_book.exec_()

class Duplicate_book_Dialog(QDialog):
    def __init__(self, book_data):
        super().__init__()

        self.setWindowTitle("שכפול הספר")
        self.setFixedSize(311, 457)

        self.initUI(book_data)

    def initUI(self, book_data):
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("main_widget")
        self.verticalLayout = QVBoxLayout(self.main_widget)

        self.verticalLayout.setObjectName("verticalLayout")

        self.details_groupBox = QGroupBox(self.main_widget)
        self.details_groupBox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.details_groupBox.setObjectName("details_groupBox")
        self.details_groupBox.setTitle("פרטים")

        self.gridLayout_2 = QGridLayout(self.details_groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.book_title_lineedit = QLineEdit(self.details_groupBox)
        self.book_title_lineedit.setObjectName("book_title_lineedit")
        self.book_title_lineedit.setText(book_data["book_title"])
        self.gridLayout_2.addWidget(self.book_title_lineedit, 0, 0, 1, 1)

        self.book_name_label = QLabel(self.details_groupBox)
        self.book_name_label.setText("שם הספר:")
        self.gridLayout_2.addWidget(self.book_name_label, 0, 1, 1, 1)

        self.series_name_lineedit = QLineEdit(self.details_groupBox)
        self.series_name_lineedit.setObjectName("series_name_lineedit")
        self.series_name_lineedit.setText(book_data["series_name"])
        self.gridLayout_2.addWidget(self.series_name_lineedit, 1, 0, 1, 1)

        self.series_name_label = QLabel(self.details_groupBox)
        self.series_name_label.setText("שם הסדרה:")
        self.gridLayout_2.addWidget(self.series_name_label, 1, 1, 1, 1)

        self.series_part_lineedit = QLineEdit(self.details_groupBox)
        self.series_part_lineedit.setObjectName("series_part_lineedit")
        self.series_part_lineedit.setText(book_data["series_part"])
        self.gridLayout_2.addWidget(self.series_part_lineedit, 2, 0, 1, 1)

        self.series_part_label = QLabel(self.details_groupBox)
        self.series_part_label.setText("חלק בסדרה:")
        self.gridLayout_2.addWidget(self.series_part_label, 2, 1, 1, 1)

        self.grade_lineedit = QLineEdit(self.details_groupBox)
        self.grade_lineedit.setObjectName("grade_lineedit")
        self.grade_lineedit.setText(book_data["grade"])
        self.gridLayout_2.addWidget(self.grade_lineedit, 3, 0, 1, 1)

        self.grade_label = QLabel(self.details_groupBox)
        self.grade_label.setText("כיתה:")
        self.gridLayout_2.addWidget(self.grade_label, 3, 1, 1, 1)

        self.age_group_lineedit = QLineEdit(self.details_groupBox)
        self.age_group_lineedit.setObjectName("age_group_lineedit")
        self.age_group_lineedit.setText(book_data["age_group"])
        self.gridLayout_2.addWidget(self.age_group_lineedit, 4, 0, 1, 1)

        self.age_group_label = QLabel(self.details_groupBox)
        self.age_group_label.setText("שכבת גיל:")
        self.gridLayout_2.addWidget(self.age_group_label, 4, 1, 1, 1)

        self.author_lineedit = QLineEdit(self.details_groupBox)
        self.author_lineedit.setObjectName("author_lineedit")
        self.author_lineedit.setText(book_data["author"])
        self.gridLayout_2.addWidget(self.author_lineedit, 5, 0, 1, 1)

        self.author_label = QLabel(self.details_groupBox)
        self.author_label.setText("מחבר:")
        self.gridLayout_2.addWidget(self.author_label, 5, 1, 1, 1)

        self.publisher_lineedit = QLineEdit(self.details_groupBox)
        self.publisher_lineedit.setObjectName("publisher_lineedit")
        self.publisher_lineedit.setText(book_data["publisher"])
        self.gridLayout_2.addWidget(self.publisher_lineedit, 6, 0, 1, 1)

        self.publisher_label = QLabel(self.details_groupBox)
        self.publisher_label.setText("מוציא לאור:")
        self.gridLayout_2.addWidget(self.publisher_label, 6, 1, 1, 1)

        self.shelf_lineedit = QLineEdit(self.details_groupBox)
        self.shelf_lineedit.setObjectName("shelf_lineedit")
        self.shelf_lineedit.setText(book_data["shelf"])
        self.gridLayout_2.addWidget(self.shelf_lineedit, 7, 0, 1, 1)

        self.shelf_label = QLabel(self.details_groupBox)
        self.shelf_label.setText("מדף:")
        self.gridLayout_2.addWidget(self.shelf_label, 7, 1, 1, 1)

        self.book_condition_combobox = QComboBox(self.details_groupBox)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.book_condition_combobox.sizePolicy().hasHeightForWidth())
        self.book_condition_combobox.setSizePolicy(sizePolicy)
        self.book_condition_combobox.setObjectName("book_condition_combobox")
        self.book_condition_combobox.addItem(book_data["book_condition"])
        self.book_condition_combobox.addItem("חדש")
        self.book_condition_combobox.addItem("משומש")
        self.book_condition_combobox.addItem("פתור/כתוב")
        self.book_condition_combobox.addItem("קרוע")
        self.book_condition_combobox.addItem("לא ידוע")
        self.gridLayout_2.addWidget(self.book_condition_combobox, 8, 0, 1, 1)

        self.book_condition_label = QLabel(self.details_groupBox)
        self.book_condition_label.setText("מצב הספר:")
        self.gridLayout_2.addWidget(self.book_condition_label, 8, 1, 1, 1)

        self.book_type_combobox = QComboBox(self.details_groupBox)
        self.book_type_combobox.setObjectName("book_type_combobox")
        self.book_type_combobox.addItem(book_data["book_type"])
        self.book_type_combobox.addItem("קודש")
        self.book_type_combobox.addItem("כתיבה")
        self.book_type_combobox.addItem("קריאה")
        self.book_type_combobox.addItem("לימוד")
        self.book_type_combobox.addItem("אחר")
        self.gridLayout_2.addWidget(self.book_type_combobox, 9, 0, 1, 1)

        self.book_type_label = QLabel(self.details_groupBox)
        self.book_type_label.setText("סוג הספר:")
        self.gridLayout_2.addWidget(self.book_type_label, 9, 1, 1, 1)

        self.remarks_lineedit = QLineEdit(self.details_groupBox)
        self.remarks_lineedit.setObjectName("remarks_lineedit")
        self.remarks_lineedit.setText(book_data["remarks"])
        self.gridLayout_2.addWidget(self.remarks_lineedit, 10, 0, 1, 1)

        self.remarks_label = QLabel(self.details_groupBox)
        self.remarks_label.setText("הערות")
        self.gridLayout_2.addWidget(self.remarks_label, 10, 1, 1, 1)

        self.verticalLayout.addWidget(self.details_groupBox)

        self.amount_frame = QFrame(self.main_widget)
        self.amount_frame.setFrameShape(QFrame.StyledPanel)
        self.amount_frame.setFrameShadow(QFrame.Raised)
        self.amount_frame.setObjectName("amount_frame")

        self.verticalLayout_2 = QVBoxLayout(self.amount_frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.amount_label = QLabel(self.amount_frame)
        self.amount_label.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft)
        self.amount_label.setText("בחר כמות:")
        self.verticalLayout_2.addWidget(self.amount_label)

        self.amount_lineedit = QLineEdit(self.amount_frame)
        self.amount_label.setText("בחר כמות:")
        self.verticalLayout_2.addWidget(self.amount_lineedit)

        self.verticalLayout.addWidget(self.amount_frame)

        self.OK_and_Cancel_buttonBox = QDialogButtonBox(self.main_widget)
        self.OK_and_Cancel_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.OK_and_Cancel_buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.OK_and_Cancel_buttonBox.setCenterButtons(True)
        self.OK_and_Cancel_buttonBox.setObjectName("OK_and_Cancel_buttonBox")
        self.verticalLayout.addWidget(self.OK_and_Cancel_buttonBox)
        self.OK_and_Cancel_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setText("ביטול")
        self.OK_and_Cancel_buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setText("אישור")
        self.gridLayout.addWidget(self.main_widget, 0, 0, 1, 1)

        self.OK_and_Cancel_buttonBox.accepted.connect(self.Duplicate_book_Ok_clicked)
        self.OK_and_Cancel_buttonBox.rejected.connect(self.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)


    def Duplicate_book_Ok_clicked(self):
        # A function to generate a 4-digit random number
        def generate_random_number():
            return str(random.randint(1000, 9999))

        # A function to check if the number already exists in the JSON file as a book_id for one of the books
        def is_number_exists(number, data):
            books_ids = []
            for book in data['books']:
                books_ids.append(book['book_id'])
            # לולאה שמבצעת את הבדיקה
            for books_id in books_ids:
                if str(books_id) == str(number):
                    return True
            return False

        selected_quantity = self.amount_lineedit.text()
        if selected_quantity == "":
            selected_quantity = 1
        # Loop to create this book in the selected quantity
        for _ in range(int(selected_quantity)):
            archive_file_content = read_archive_json()
            while True:
                random_number = generate_random_number()
                if not is_number_exists(random_number, archive_file_content):
                    break
            self.remarks = self.remarks_lineedit.text().strip()
            self.book_type = self.book_type_combobox.currentText().strip()
            if self.book_type == "בחר סוג ספר":
                self.book_type = "לא נבחר"
            self.book_condition = self.book_condition_combobox.currentText().strip()
            if self.book_condition == "בחר מצב ספר":
                self.book_condition = "לא נבחר"
            self.shelf = self.shelf_lineedit.text().strip()
            self.publisher = self.publisher_lineedit.text().strip()
            self.author = self.author_lineedit.text().strip()
            self.age_group = self.age_group_lineedit.text().strip()
            self.grade = self.grade_lineedit.text().strip()
            self.series_part = self.series_part_lineedit.text().strip()
            self.series_name = self.series_name_lineedit.text().strip()
            self.book_title = self.book_title_lineedit.text().strip()
            self.book_id = str(random_number)

            self.create_new_books()

        self.close()

    def create_new_books(self):
        archive_file_content = read_archive_json()
        # Create a new book object
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
        # Add the new book to the dictionary variable that contains all the books
        archive_file_content['books'].append(new_book)
        # Update the file with the updated dictionary variable
        write_update_to_the_archive_json(archive_file_content)


class editing_book_details_dialog(QDialog):
    def __init__(self, book_data):
        super().__init__()

        self.Creating_a_editing_book_details_dialog_GUI(book_data)

    def Creating_a_editing_book_details_dialog_GUI(self, book_data):
        self.this_original_book_id = book_data["book_id"]
        self.setWindowTitle(f"עריכת ספר {self.this_original_book_id}")
        self.setFixedSize(400, 600)
        self.setWindowIcon(QIcon('dependence/images/edit_book.png'))

        # Creating the main layout/tunnel/תַסדִיר according to which all components will be arranged
        # In this case, they will be: save_button, cancel_button, row_layout
        layout = QVBoxLayout()

        # An array to contain the QLineEdit and QComboBox widgets in the window
        self.widgets_dict = {}

        # An array that contains the text to be given to the labels
        labels_names = [
            "מְזַהָה סֵפֶר",
            "שָׂם הַסֵּפֶר",
            "שָׂם הַסִּדְרָה",
            "חֵלֶק בְּסִדְרָה",
            "כִּתָּה",
            "שִׁכְבַת גִּיל",
            "מְחַבֵּר",
            "מוֹצִיא לָאוֹר",
            "מַדָּף",
            "כְּמוֹת בְּאַרְכִיּוֹן",
            "מֻשְׁאָל",
            "מַצַּב הַסֵּפֶר",
            "תַּאֲרִיךְ הַהַשְׁאָלָה",
            "סוּג הַסֵּפֶר",
            "שֵׁם הַשּׁוֹאֵל/הַלּוֹקֵחַ",
            "תְּעוּדַת זֶהוּת",
            "הֶעָרוֹת"
        ]

        # A loop that creates a QLabel and a QLineEdit
        for key, value in enumerate(book_data):
            # Creating labels
            label = QLabel(labels_names[key] + ":")
            # Condition only for the label of book_id
            if value == "book_id":
                label.setText(labels_names[key] + " (לֹא מֻמְלַץ לְשַׁנּוֹת):")
                label.setStyleSheet("color: red;")

            # If the key is not "book_type" or "book_condition", QLineEdit will be created and added to the layout
            if value not in ["book_type", "book_condition"]:
                edit_line = QLineEdit(book_data[value])
                # Creating a QHBoxLayout and adding the label and LineEdit to it
                row_layout = QHBoxLayout()
                row_layout.addWidget(edit_line)
                row_layout.addWidget(label)
                # Adding the HBoxLayout to the main layout
                layout.addLayout(row_layout)
                # Add edit_line to the widgets dictionary
                self.widgets_dict[value] = edit_line
            # For the data "book_type" or "book_condition", creates a QComboBox
            elif value == "book_condition":
                # Creating a QComboBox for book_condition and adding it to the layout
                combo_box = QComboBox()
                if not value in ["חדש", "משומש", "פתור/כתוב", "קרוע", "לא ידוע"]:
                    combo_box.addItem(book_data[value])
                combo_box.addItem("חדש")
                combo_box.addItem("משומש")
                combo_box.addItem("פתור/כתוב")
                combo_box.addItem("קרוע")
                combo_box.addItem("לא ידוע")
                combo_box.setCurrentText(book_data[value])
                # Creating a QHBoxLayout and adding the label and ComboBox to it
                row_layout = QHBoxLayout()
                row_layout.addWidget(combo_box)
                row_layout.addWidget(label)
                # Adding the HBoxLayout to the main layout
                layout.addLayout(row_layout)
                # Add combo_box to the widgets dictionary
                self.widgets_dict[value] = combo_box
            elif value == "book_type":
                # Creating a QComboBox for book_type and adding it to the layout
                combo_box = QComboBox()
                if not value in ["קודש", "כתיבה", "קריאה", "לימוד"]:
                    combo_box.addItem(book_data[value])
                combo_box.addItem("קודש")
                combo_box.addItem("כתיבה")
                combo_box.addItem("קריאה")
                combo_box.addItem("לימוד")
                combo_box.addItem("אחר")
                combo_box.setCurrentText(book_data[value])
                # Creating a QHBoxLayout and adding the label and ComboBox to it
                row_layout = QHBoxLayout()
                row_layout.addWidget(combo_box)
                row_layout.addWidget(label)

                # Adding the HBoxLayout to the main layout
                layout.addLayout(row_layout)
                # Add combo_box to the widgets dictionary
                self.widgets_dict[value] = combo_box

        self.setLayout(layout)

        # Create a "Save" button
        save_button = QPushButton("שמור", self)
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)
        # Create a "Cancel" button
        cancel_button = QPushButton("בטל", self)
        cancel_button.clicked.connect(self.accept)
        layout.addWidget(cancel_button)

    def save_changes(self):
        # Building a dictionary to store the current content in the input fields
        user_input_dict = {key: (widget.text() if isinstance(widget, QLineEdit) else widget.currentText()) for
                           key, widget in self.widgets_dict.items()}

        # Check if the user change the book id field
        if user_input_dict["book_id"] != self.this_original_book_id:
            archive_file_content = read_archive_json()
            for book in archive_file_content["books"]:
                # Check if there is another book with the chosen id
                if book["book_id"] == user_input_dict["book_id"]:
                    # The error message
                    error_message = f"המזהה החדש שבחרת הינו כבר בשימוש ע\"י ספר אחר,\nשינוי המזהה {self.this_original_book_id} לא עבר בהצלחה"
                    # Error message window
                    error_box = QtWidgets.QMessageBox()
                    error_box.setIcon(QtWidgets.QMessageBox.Critical)
                    error_box.setWindowTitle("שגיאה")
                    error_box.setText(error_message)
                    # Display the message to the user
                    error_box.exec_()
                user_input_dict["book_id"] = self.this_original_book_id

        # Locating the current book in the archive and injecting its details update
        archive_file_content = read_archive_json()
        for i, book in enumerate(archive_file_content["books"]):
            # Locating the book by its ID
            if book["book_id"] == self.this_original_book_id:
                archive_file_content["books"][i] = user_input_dict
                break

        # Here you can save the updated information to the JSON file
        write_update_to_the_archive_json(archive_file_content)

        # Close the dialog
        self.accept()

class Add_new_books_dialog(QDialog):
    def __init__(self):
        super().__init__()

        self.Creating_a_add_new_books_dialog_GUI()

    def Creating_a_add_new_books_dialog_GUI(self):
        self.setWindowTitle("הוספת ספרים")
        self.setFixedSize(350, 650)
        self.setWindowIcon(QIcon('dependence/images/add_books.png'))

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Creating all widgets
        self.title_label = QLabel("שם הספר:")
        layout.addWidget(self.title_label)
        self.book_title_lineedit = QLineEdit()
        layout.addWidget(self.book_title_lineedit)

        self.series_name_label = QLabel("שם הסדרה:")
        layout.addWidget(self.series_name_label)
        self.series_name_lineedit = QLineEdit()
        layout.addWidget(self.series_name_lineedit)

        self.series_part_label = QLabel("חלק בסדרה:")
        layout.addWidget(self.series_part_label)
        self.series_part_lineedit = QLineEdit()
        layout.addWidget(self.series_part_lineedit)

        self.grade_label = QLabel("כיתה:")
        layout.addWidget(self.grade_label)
        self.grade_lineedit = QLineEdit()
        layout.addWidget(self.grade_lineedit)

        self.age_group_label = QLabel("שכבת גיל:")
        layout.addWidget(self.age_group_label)
        self.age_group_lineedit = QLineEdit()
        layout.addWidget(self.age_group_lineedit)

        self.author_label = QLabel("מחבר:")
        layout.addWidget(self.author_label)
        self.author_lineedit = QLineEdit()
        layout.addWidget(self.author_lineedit)

        self.publisher_label = QLabel("מוציא לאור:")
        layout.addWidget(self.publisher_label)
        self.publisher_lineedit = QLineEdit()
        layout.addWidget(self.publisher_lineedit)

        self.shelf_label = QLabel("מדף:")
        layout.addWidget(self.shelf_label)
        self.shelf_lineedit = QLineEdit()
        layout.addWidget(self.shelf_lineedit)

        self.book_condition_label = QLabel("מצב הספר:")
        layout.addWidget(self.book_condition_label)
        self.book_condition_combobox = QComboBox()
        self.book_condition_combobox.addItems(["בחר מצב ספר", "חדש", "משומש", "פתור/כתוב", "קרוע", "לא ידוע"])
        layout.addWidget(self.book_condition_combobox)

        self.book_type_label = QLabel("סוג הספר:")
        layout.addWidget(self.book_type_label)
        self.book_type_combobox = QComboBox()
        self.book_type_combobox.addItems(["בחר סוג ספר", "קודש", "כתיבה", "קריאה", "לימוד", "אחר"])
        layout.addWidget(self.book_type_combobox)

        self.remarks_label = QLabel("הערות:")
        layout.addWidget(self.remarks_label)
        self.remarks_lineedit = QLineEdit()
        layout.addWidget(self.remarks_lineedit)

        self.amount_label = QLabel("כמות:")
        layout.addWidget(self.amount_label)
        self.amount_lineedit = QLineEdit()
        layout.addWidget(self.amount_lineedit)
        # Limiting input to digits only
        amount_validator = QIntValidator()
        self.amount_lineedit.setValidator(amount_validator)

        # Create a "Save" button
        self.save_button = QPushButton("שמור")
        self.save_button.clicked.connect(self.save_button_clicked)
        layout.addWidget(self.save_button)


    def save_button_clicked(self):
        # A function to generate a 4-digit random number
        def generate_random_number():
            return str(random.randint(1000, 9999))

        # A function to check if the number already exists in the JSON file as a book_id for one of the books
        def is_number_exists(number, data):
            books_ids = []
            for book in data['books']:
                books_ids.append(book['book_id'])
            # לולאה שמבצעת את הבדיקה
            for books_id in books_ids:
                if str(books_id) == str(number):
                    return True
            return False

        selected_quantity = self.amount_lineedit.text()
        if selected_quantity == "":
            selected_quantity = 1
        # Loop to create this book in the selected quantity
        for _ in range(int(selected_quantity)):
            archive_file_content = read_archive_json()
            while True:
                random_number = generate_random_number()
                if not is_number_exists(random_number, archive_file_content):
                    break
            self.remarks = self.remarks_lineedit.text().strip()
            self.book_type = self.book_type_combobox.currentText().strip()
            if self.book_type == "בחר סוג ספר":
                self.book_type = "לא נבחר"
            self.book_condition = self.book_condition_combobox.currentText().strip()
            if self.book_condition == "בחר מצב ספר":
                self.book_condition = "לא נבחר"
            self.shelf = self.shelf_lineedit.text().strip()
            self.publisher = self.publisher_lineedit.text().strip()
            self.author = self.author_lineedit.text().strip()
            self.age_group = self.age_group_lineedit.text().strip()
            self.grade = self.grade_lineedit.text().strip()
            self.series_part = self.series_part_lineedit.text().strip()
            self.series_name = self.series_name_lineedit.text().strip()
            self.book_title = self.book_title_lineedit.text().strip()
            self.book_id = str(random_number)

            self.create_new_books()

        self.close()

    def create_new_books(self):
        archive_file_content = read_archive_json()
        # Create a new book object
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
        # Add the new book to the dictionary variable that contains all the books
        archive_file_content['books'].append(new_book)
        # Update the file with the updated dictionary variable
        write_update_to_the_archive_json(archive_file_content)

class Are_you_sure_window(QDialog):
    def __init__(self, books_ids):
        super().__init__()

        self.Creating_a_Add_new_books_dialog_GUI(books_ids)

    def Creating_a_Add_new_books_dialog_GUI(self, books_ids):
        self.sure_to_delete = False
        List_of_books_awaiting_deletion_approval = []
        self.setWindowTitle('ספרים למחיקה')
        self.setFixedSize(600, 300)
        self.setWindowIcon(QIcon('dependence/images/delete_book.png'))

        layout = QVBoxLayout(self)

        # Create a label
        label = QLabel("האם אתה בטוח שברצונך להסיר את הספרים הבאים מן הארכיון:")
        layout.addWidget(label)

        # Add a scroll box
        scroll_area = QScrollArea()
        layout.addWidget(scroll_area)

        # text box into the scroll box
        text_widget = QWidget()
        scroll_area.setWidget(text_widget)

        text_layout = QVBoxLayout(text_widget)

        archive_file_content = read_archive_json()

        for book in archive_file_content["books"]:
            for id in books_ids:
                if book['book_id'] == id:
                    Book_details = (book['book_id'] + ", " + book['book_title'] + ", " + book['book_type'] + ", " + book['grade']
                         + ", " + book['age_group'] + ", " + book['author'] + ", " + book['publisher']
                         + ", " + book['series_name'] + ", " + book['series_part'] + ", " + book['shelf']
                         + ", " + book['amount_in_archive'] + ", " + book['book_condition']
                         + ", " + book['remarks'] + ", ")
                    List_of_books_awaiting_deletion_approval.append(Book_details)

        # Adding the books details to the text box
        for name in List_of_books_awaiting_deletion_approval:
            name_label = QLabel(name)
            name_label.setAlignment(QtCore.Qt.AlignTop)
            text_layout.insertWidget(1, name_label)

        text_widget.setLayout(text_layout)
        scroll_area.setWidgetResizable(True)

        # row for buttons
        buttons_layout = QHBoxLayout()

        # Added a "Yes" button
        yes_button = QPushButton("כן", self)
        yes_button.clicked.connect(self.on_yes_click)
        # Added a "No" button
        no_button = QPushButton("לא", self)
        no_button.clicked.connect(self.accept)

        # Adding the buttons to the button layout
        buttons_layout.addWidget(yes_button)
        buttons_layout.addWidget(no_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def on_yes_click(self):
        self.sure_to_delete = True
        self.accept()

class Is_book_returned_dialog(QDialog):
    def __init__(self, book_data):
        super().__init__()
        self.setWindowTitle("האם הספר מוחזר?")
        self.resize(390, 163)
        self.setWindowIcon(QIcon('dependence/images/nook_return.png'))

        self.main_widget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.main_widget)

        font = QtGui.QFont()
        font.setPointSize(12)

        current_book_borrower_name = book_data["borrower_name"]
        current_book_name = book_data["book_title"]

        self.is_book_return_label = QLabel(f"האם התלמיד {current_book_borrower_name} החזיר את הספר \"{current_book_name}\"?", self.main_widget)
        self.is_book_return_label.setFont(font)
        self.verticalLayout.addWidget(self.is_book_return_label)

        self.delete_remarks_check_box = QCheckBox("למחוק הערות", self.main_widget)
        self.delete_remarks_check_box.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.verticalLayout.addWidget(self.delete_remarks_check_box)

        self.yes_and_no_button_box = QDialogButtonBox(QtCore.Qt.Horizontal, self.main_widget)
        self.yes_and_no_button_box.setStandardButtons(QDialogButtonBox.No | QDialogButtonBox.Yes)
        self.yes_and_no_button_box.button(QtWidgets.QDialogButtonBox.No).setText("לא")
        self.yes_and_no_button_box.button(QtWidgets.QDialogButtonBox.Yes).setText("כן")
        self.verticalLayout.addWidget(self.yes_and_no_button_box)

        self.setLayout(self.verticalLayout)

        self.yes_and_no_button_box.accepted.connect(self.accept)
        self.yes_and_no_button_box.rejected.connect(self.reject)
class Borrower_details_dialog(QDialog):
    def __init__(self, book_remarks):
        super().__init__()

        self.Creating_a_Borrower_details_dialog_GUI(book_remarks)

    def Creating_a_Borrower_details_dialog_GUI(self, book_remarks):
        self.Book_loan_approval = False
        self.setWindowTitle('פרטי השואל/הלוקח')
        self.setFixedSize(350, 300)
        self.setWindowIcon(QIcon('dependence/images/book_lend.png'))

        self.gridLayout = QGridLayout(self)
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
        self.remarks_lineEdit.setText(book_remarks)

        self.verticalLayout_3.addWidget(self.remarks_lineEdit)
        self.verticalLayout.addWidget(self.remarks_frame)

        self.gridLayout.addWidget(self.main_frame, 0, 0, 1, 1)

        self.OK_and_Cancel_buttonBox = QtWidgets.QDialogButtonBox(self)
        self.OK_and_Cancel_buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.OK_and_Cancel_buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.OK_and_Cancel_buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setText("ביטול")
        self.OK_and_Cancel_buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setText("אישור")

        self.gridLayout.addWidget(self.OK_and_Cancel_buttonBox, 1, 0, 1, 1)

        # Assign a function to clicking the "OK" button
        self.OK_and_Cancel_buttonBox.accepted.connect(self.Ok_clicked)
        self.OK_and_Cancel_buttonBox.rejected.connect(self.reject)

    def Ok_clicked(self):
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
        self.Book_loan_approval = True
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    icon = QIcon("dependence\images\Software icon.png")  # החלף את "path_to_your_icon_file.png" בנתיב לקובץ האיקון שלך
    window.setWindowIcon(icon)
    # Display the window in full screen
    window.showMaximized()

    sys.exit(app.exec_())
