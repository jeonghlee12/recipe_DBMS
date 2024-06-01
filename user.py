class User:
    """
    Bare skeleton code for User class
    """
    def __init__(self, id, firstname, lastname, role) -> None:
        self.ID = id
        self.FirstName = firstname
        self.LastName = lastname
        self.role = role

class PremiumUser(User):
    def __init__(self, id, firstname, lastname, role) -> None:
        super().__init__(id, firstname, lastname, role)

class Admin(PremiumUser):
    def __init__(self, id, firstname, lastname, role) -> None:
        super().__init__(id, firstname, lastname, role)