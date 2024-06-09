import bcrypt
import psycopg2
from user import User

from database_setup import establish_connection

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def add_user(firstname: str, lastname: str, email: str, username: str, password: str, role: str = None) -> bool:
    ### hash password using bcrypt package
    # create salt
    salt = bcrypt.gensalt()

    # hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # change it to string
    hashed_password = hashed_password.decode('utf-8')

    ### add user to db
    conn = establish_connection()
    if conn is None:
        print("*" * 70)
        print("No connection to PostgreSQL!")
        return False
    
    try:
        cursor = conn.cursor()

        if role:
            cursor.execute(f"INSERT INTO recipe.Users (username, email, password_hash, firstname, lastname, role) VALUES ('{username}', '{email}', '{hashed_password}', '{firstname}', '{lastname}', '{role}')")
        else:
            cursor.execute(f"INSERT INTO recipe.Users (username, email, password_hash, firstname, lastname) VALUES ('{username}', '{email}', '{hashed_password}', '{firstname}', '{lastname}')")
        return True
        
    except psycopg2.Error as e:
        conn.rollback()
        print("*" * 70)
        print("An error occurred with PostgreSQL")
        print(e)
        return False
    
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def authenticate_user(username_or_email: str, password: str) -> User:
    conn = establish_connection()
    if conn is None:
        print("No connection to PostgreSQL!")
        return None
    
    try:
        cursor = conn.cursor()

        # find user
        cursor.execute(f"SELECT userid, username, email, password_hash, firstname, lastname, role FROM recipe.Users WHERE username = '{username_or_email}' OR email = '{username_or_email}'")
        user = cursor.fetchone()

        # if user exists
        if user:
            user_id, username, email, hashed_password, firstname, lastname, role = user
            # check password
            if check_password(password, hashed_password):
                return User(id=user_id, username=username, email=email, firstname=firstname, lastname=lastname, role=role, password_hash=hashed_password)
            else:
                print("Invalid password!")
                return None
        # otherwise, user not found
        else:
            print("User not found")
            return None

    except psycopg2.Error as e:
        conn.rollback()
        print("*" * 70)
        print("An error occurred with PostgreSQL")
        print(e)
        return None

    finally:
        conn.commit()
        cursor.close()
        conn.close()