class User:
    """
    Bare skeleton code for User class
    """
    def __init__(self, id: int, username: str, email: str, firstname: str, lastname: str, role: str) -> None:
        self.ID = id
        self.username = username
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.role = role
