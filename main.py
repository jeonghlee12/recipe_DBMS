import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QVBoxLayout, QLineEdit, QLabel, QPushButton, QWidget

class recipeAppUI(QMainWindow):


    def __init__(self, parent = None):
        super().__init__(parent)
        
        # setup PostgreSQL connection
        self.connectDB()

        # check if RecipeDB schema exists, otherwise create them
        self.check_DB()
        
        # create window specification
        self.setWindowTitle("Recipe DB Application")
        self.widget = QWidget()
        self.layout = QVBoxLayout()

        self.username_label = QLabel('Username')
        self.layout.addWidget(self.username_label)

        self.username_input = QLineEdit(self)
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel('Password')
        self.layout.addWidget(self.password_label)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.check_credentials)
        self.layout.addWidget(self.login_button)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)


    def check_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Replace these lines with your actual authentication logic

        query = QSqlQuery()
        query.exec(
        f"""SELECT COUNT(*) FROM Recipe.users WHERE username = '{username}' AND password = '{password}';"""
        )
        query.first()
        authenticated = query.value(0)
        if authenticated:
            QMessageBox.information(self, 'Success', 'You are logged in')
        else:
            QMessageBox.warning(self, 'Error', 'Bad username or password')

    
    def connectDB(self):
        """Establishes connection to the PostgreSQL DB

        Default connection parameters are as follows
        Database: postgres
        Hostname: localhost
        Username: postgres
        Password: postgres

        """
        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setDatabaseName("postgres")
        self.db.setHostName("localhost")

        # establish PSQL connection, otherwise, exit
        if not self.db.open("postgres", "postgres"):
            QMessageBox.critical(self, "PostgreSQL connection error", self.db.lastError().databaseText())
            self.db.close()
            sys.exit(1)

    def check_DB(self):
        """Checks PSQL if required schemas exists.
        If not, creates all relevant schemas.

        Args:
            db: QSqlDatabase connection object to the PostgreSQL DB.

        """
        if not self.db.transaction():
            QMessageBox.critical(self, "Failed to authenticate RecipeDB", self.db.lastError().databaseText())
            self.db.close()
            sys.exit(1)

        query = QSqlQuery()

        # Create first table
        query.exec_("""
            CREATE SCHEMA IF NOT EXISTS Recipe;
            CREATE TABLE IF NOT EXISTS Recipe.users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
            INSERT INTO Recipe.users VALUES (1, 'admin', 'Admin') ON CONFLICT DO NOTHING;
        """)

        if not query.isActive():
            self.db.rollback()
            QMessageBox.critical(self, "Failed to authenticate RecipeDB", f"Failed to authenticate 'users' table:\n{query.lastError().text()}")
            self.db.close()
            sys.exit(1)
        
        if not self.db.commit():
            QMessageBox.critical(self, "Failed to authenticate RecipeDB", query.lastError().databaseText())
            self.db.close()
            sys.exit(1)


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = recipeAppUI()
    window.show()
    sys.exit(app.exec_())