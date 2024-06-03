import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QHBoxLayout, QDialog, QGridLayout, QMenu, QLabel, QPushButton, QWidget, QAction

from loginUI import LoginDialog
from adminMenuUI import adminMenu

class recipeApp(QMainWindow):
    """
    Main UI application
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        
        # Login first before initialization main window
        self.showLogin()

        # create window specification
        self.setWindowTitle("Recipe DB Application")
        self.setMinimumSize(700, 700)

        self.main_widget = QWidget()
        self.main_layout = QGridLayout()

        self.header_title = self.user_header()
        self.main_layout.addWidget(self.header_title, 0, 3, 1, -1)

        self.menu_widget = self.homeMenu()
        self.main_layout.addWidget(self.menu_widget, 1, 0, 15, 4)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)


    def showLogin(self):
        """Calls the login dialog
        """
        ld = LoginDialog(self)

        # if login was successful, retrieve user information
        if ld.exec_() == QDialog.Accepted:
            self.user = ld.getUser()
        else: # if login window closed without actual login, close application
            QSqlDatabase.database().close()
            sys.exit(0)
    
    def user_header(self):
        text = self.user.FirstName + " " + self.user.LastName
        if self.user.role == 'admin':
            text += " (administrator)"
        elif self.user.role == 'premium':
            text += " (premium user)"
        
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(text))

        settings_button = QPushButton("Settings")
        settings_button.setMenu(self.create_settings_menu())
        header_layout.addWidget(settings_button)

        header_widget.setLayout(header_layout)
        return header_widget
    
    def create_settings_menu(self):
        # Create the menu
        menu = QMenu()

        # Add actions to the menu
        change_username_action = QAction("Change Username", self)
        # change_username_action.triggered.connect(self.change_username)

        change_password_action = QAction("Change Password", self)
        # change_password_action.triggered.connect(self.change_password)

        menu.addAction(change_username_action)
        menu.addAction(change_password_action)

        return menu

    def homeMenu(self):
        if self.user.role == 'admin':
            return adminMenu(self.user)
        elif self.user.role == 'premium':
            return None
        else: return None


def DB_error(error_title):
    """Shows error dialog for any fatal DB related errors.
    
    Further, closes application since errors are fatal.
    """
    QMessageBox.critical(None, error_title, QSqlDatabase.database().lastError().databaseText())
    QSqlDatabase.database().close()
    sys.exit(1)



