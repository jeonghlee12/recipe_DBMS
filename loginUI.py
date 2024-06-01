from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QGridLayout, QPushButton, QMessageBox
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtCore import Qt

from user import User, PremiumUser, Admin

class LoginDialog(QDialog):
    """
    Login page before main application is launched
    """    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 200)
        self.setWindowTitle('Login')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QGridLayout(self)

        layout.addWidget(QLabel('Username:'), 0, 0)
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input, 0, 1)

        layout.addWidget(QLabel('Password:'), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input, 1, 1)

        self.connect_button = QPushButton('Login', enabled=False)
        layout.addWidget(self.connect_button, 2, 0, 1, 2)

        self.connect_button.clicked.connect(self.check_credentials)
        self.username_input.textChanged.connect(self.checkFields)
        self.password_input.textChanged.connect(self.checkFields)

    def checkFields(self):
        if self.username_input.text() and self.password_input.text():
            self.connect_button.setEnabled(True)
        else:
            self.connect_button.setEnabled(False)
    
    def check_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()

        query = QSqlQuery()
        query.exec(
        f"""SELECT * FROM Recipe.users WHERE username = '{username}' AND password = '{password}';"""
        )
        query.first()
        authenticated = query.value(0)
        if authenticated:
            user_att = {}
            for att in ['id', 'username', 'password', 'role']:
                fieldNo = query.record().indexOf(att)
                user_att[att] = query.value(fieldNo)
            if user_att['role'] == 'admin':
                self.user = Admin(user_att['id'], user_att['username'], user_att['password'], user_att['role'])
            elif user_att['role'] == 'premium':
                self.user = PremiumUser(user_att['id'], user_att['username'], user_att['password'], user_att['role'])
            else:
                self.user = User(user_att['id'], user_att['username'], user_att['password'], user_att['role'])
            query.finish()
            self.accept()
        if not authenticated:
            QMessageBox.warning(self, 'Error', 'Bad username or password')
    
    def getUser(self):
        return self.user