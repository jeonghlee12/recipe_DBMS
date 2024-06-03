import bcrypt
import psycopg2
from user import User

from database_setup import establish_connection

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def add_user(firstname: str, lastname: str, email: str, username: str, password: str, role: str = None) -> None:
    ### hash password using bcrypt package
    # create salt
    salt = bcrypt.gensalt()

    # hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # change it to string
    hashed_password = hashed_password.decode('utf-8')

    ### add user to db
    try:
        conn = establish_connection()
        cursor = conn.cursor()

        cursor.execute(f"INSERT INTO recipe.Users (username, email, password_hash, firstname, lastname) VALUES ('{username}', '{email}', '{hashed_password}', '{firstname}', '{lastname}')")

        conn.commit()
        cursor.close()
        conn.close()
    
    except psycopg2.errors.UniqueViolation as uv:
        print(f"User {firstname} {lastname} with username '{username}' and email '{email}' already exists!\n")

    except Exception as e:
        print(f"An error occurred: {e}")

def authenticate_user(username_or_email: str, password: str) -> User:
    try:
        conn = establish_connection()
        cursor = conn.cursor()

        # find user
        cursor.execute(f"SELECT username, email, password_hash, firstname, lastname, role FROM recipe.Users WHERE username = {username_or_email} OR email = {username_or_email}")
        user = cursor.fetchone()

        # if user exists
        if user:
            user_id, username, email, hashed_password, firstname, lastname, role = user
            # check password
            if check_password(password, hashed_password):
                return User(user_id, firstname, lastname, role, username, email, hashed_password)
            else:
                print("Invalid password!")
                return None
        # otherwise, user not found
        else:
            print("User not found")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        conn.commit()
        cursor.close()
        conn.close()