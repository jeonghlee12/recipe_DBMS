import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDesktopWidget, QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QWidget

from loginUI import LoginDialog

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
        self.setMinimumSize(500, 500)

        # 일단 로그인 하면 "Welcome {이름}"만 표시하도록 함
        self.widget = QLabel("Welcome " + self.user.FirstName + "!")
        self.setCentralWidget(self.widget)


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
    

def DB_error(error_title):
    """Shows error dialog for any fatal DB related errors.
    
    Further, closes application since errors are fatal.
    """
    QMessageBox.critical(None, error_title, QSqlDatabase.database().lastError().databaseText())
    QSqlDatabase.database().close()
    sys.exit(1)



