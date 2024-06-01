import sys
from PyQt5.QtWidgets import QApplication
import recipeAppUI
import database_setup

def main():
    app = QApplication([])

    # establish DB connection
    if not database_setup.connectDB():
        recipeAppUI.DB_error("PostgreSQL connection error")
    if not database_setup.initialize_DB():
        recipeAppUI.DB_error("Failed to authenticate RecipeDB")

    window = recipeAppUI.recipeApp()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()