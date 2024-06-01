from PyQt5.QtSql import QSqlDatabase, QSqlQuery

def connectDB():
        """Establishes connection to the PostgreSQL DB

        Default connection parameters are as follows
        Database: postgres
        Hostname: localhost
        Username: postgres
        Password: postgres

        Returns:
            Connection status of program
        """
        DB_name = 'postgres'
        hostname = 'localhost'
        username = 'postgres'
        password = 'postgres'

        db = QSqlDatabase.addDatabase("QPSQL")
        db.setDatabaseName(DB_name)
        db.setHostName(hostname)

        # establish PSQL connection: returns true if successful
        return db.open(username, password)

def initialize_DB():
    """Checks PSQL if required schemas exists.
    If not, creates all relevant schemas.

    Args:
        db: QSqlDatabase connection object to the PostgreSQL DB.

    Returns:
        True if DB initialization is successful. If any error occurs, False
    """
    db = QSqlDatabase.database()
    if not db.transaction():
        return False

    query = QSqlQuery()

    # Create first table
    query.exec_("""
        CREATE SCHEMA IF NOT EXISTS Recipe;
        CREATE TABLE IF NOT EXISTS Recipe.users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
        INSERT INTO Recipe.users VALUES (1, 'admin', 'Admin', 'admin') ON CONFLICT DO NOTHING;
    """)

    if not query.isActive():
        db.rollback()
        return False
    
    if not db.commit():
        return False
    
    return True