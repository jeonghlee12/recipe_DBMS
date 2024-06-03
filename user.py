from database_setup import establish_connection
import bcrypt

class User:
    """
    Bare skeleton code for User class
    """
    def __init__(self, id: int, username: str, email: str, firstname: str, lastname: str, role: str, password_hash: str) -> None:
        self.ID = id
        self.username = username
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.role = role
        self.hashed_password = password_hash

    def authenticate(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

    def modify_username(self, new_username: str, password: str) -> None:
        if self.authenticate(password):
            try:
                conn = establish_connection()
                cursor = conn.cursor()

                # find if duplicate username exists
                cursor.execute(f"SELECT username FROM recipe.Users WHERE username = '{new_username}'")
                user = cursor.fetchone()
                
                # if exists
                if user:
                    print(f"User with '{new_username}' already exists!")
                # otherwise, update
                else:
                    cursor.execute(f"UPDATE recipe.Users SET username = '{new_username}' WHERE userID = {self.ID}")
                    self.username = new_username
                    

            except Exception as e:
                print(f"An error occurred: {e}")

            finally:
                conn.commit()
                cursor.close()
                conn.close()
    
    def modify_email(self, new_email: str, password: str) -> None:
        if self.authenticate(password):
            try:
                conn = establish_connection()
                cursor = conn.cursor()

                # find if duplicate email exists
                cursor.execute(f"SELECT email FROM recipe.Users WHERE email = '{new_email}'")
                user = cursor.fetchone()

                # if exists
                if user:
                    print(f"User with '{new_email}' already exists!")
                # otherwise, update
                else:
                    cursor.execute(f"UPDATE recipe.Users SET email = '{new_email}' WHERE userID = {self.ID}")
                    self.email = new_email
                    

            except Exception as e:
                print(f"An error occurred: {e}")

            finally:
                conn.commit()
                cursor.close()
                conn.close()

    def modify_password(self, new_password: str, password: str) -> None:
        if self.authenticate(password):
            try:
                conn = establish_connection()
                cursor = conn.cursor()

                salt = bcrypt.gensalt()

                # hash the password
                new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)

                # change it to string
                new_hashed_password = new_hashed_password.decode('utf-8')

                # update
                cursor.execute(f"UPDATE recipe.Users SET password_hash = '{new_hashed_password}' WHERE userID = {self.ID}")
                self.hashed_password = new_hashed_password
                    
            except Exception as e:
                print(f"An error occurred: {e}")

            finally:
                conn.commit()
                cursor.close()
                conn.close()