# imports for terminal interface
import os
import time
from shutil import get_terminal_size

from database_setup import create_db, initialize_db
import scenarios


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    terminal_width = get_terminal_size()[0] - 1
    print("-" * terminal_width)
    print("Accessing Recipe Database")
    print("*" * 55)
    db_exists = input("Is there an existing database to connect to? (Y\\N): ")
    if (db_exists != "Y" and db_exists != "y"):
        print("Creating and initializing database...")
        create_db()
        initialize_db()
        print("...Database successfully created and initialized!")
    print("...Connected to database!")
    print("-" * terminal_width)
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')

    print("-" * terminal_width)
    print("Recipe Database Management System")
    print("No login profile: please log in")
    print("*" * 70)
    print('Available operations (* marked operations are available after login)')
    print("0. Create account")
    print("1. Login")
    print("2. Search for a recipe")
    print("3. View recipe ranking list by highest average rating")
    print("4. View highest average rated recipes by recipe type")
    print("5. *View recommended recipe list")
    print("6. **Edit recipe (premium users and up only)")
    print("7. ***View recipe edit requests (administrator only)")
    print("8. *View my profile")
    print("9. *Change my profile")
    print("-" * 30)
    print("Available operations when viewing a recipe (requires login)")
    print("- *Bookmark this recipe")
    print("- *Rate this recipe")
    print("*" * 70)
    user_input = input("Select an operation number (type 'q' to exit): ")

    while not user_input.isnumeric() and user_input != 'q':
        user_input = input("Invalid input. Please type a valid operation number (type 'q' to exit): ")
    
    
    user = None
    while (user_input != 'q'):
        time.sleep(0.5)
        os.system('cls' if os.name == 'nt' else 'clear')
        print("-" * terminal_width)
        print("Recipe Database Management System")
        print("*" * 70)

        user_num = int(user_input)
        if user_num == 0:
            scenarios.create_account()
        elif user_num == 1:
            user = scenarios.login()
        elif user_num == 2:
            scenarios.recipe_search(user)
        elif user_num == 3:
            scenarios.get_popular_recipes(user)
        elif user_num == 4:
            scenarios.get_partitioned_recipes(user)
        elif user_num == 5:
            scenarios.get_recommended_recipe(user)
        elif user_num == 6:
            scenarios.edit_recipe(user)
        elif user_num == 7:
            scenarios.approve_recipe_edit(user)
        elif user_num == 8:
            scenarios.view_profile(user)
        elif user_num == 9:
            scenarios.change_profile(user)
        elif user_num == 10:
            user = None
            os.system('cls' if os.name == 'nt' else 'clear')
            
        print("-" * terminal_width)
        print("Recipe Database Management System")
        if user:
            print(f"Welcome {user.firstname} (level: {user.role})")
            print("*" * 70)
            print('Available operations')
            print("1. Login")
            print("2. Search for a recipe")
            print("3. View recipe ranking list by highest average rating")
            print("4. View highest average rated recipes by recipe type")
            print("5. *View recommended recipe list")
            print("6. **Edit recipe (premium users and up only)")
            print("7. ***View recipe edit requests (administrator only)")
            print("8. *View my profile")
            print("9. *Change my profile")
            print("10. Logout")
            print("-" * 30)
            print("Available operations when viewing a recipe")
            print("- *Bookmark this recipe")
            print("- *Rate this recipe")
        else:
            print("No login profile: please log in")
            print("*" * 70)
            print('Available operations (* marked operations are available after login)')
            print("0. Create account")
            print("1. Login")
            print("2. Search for a recipe")
            print("3. View recipe ranking list by highest average rating")
            print("4. View highest average rated recipes by recipe type")
            print("5. *View recommended recipe list")
            print("6. **Edit recipe (premium users and up only)")
            print("7. ***View recipe edit requests (administrator only)")
            print("8. *View my profile")
            print("9. *Change my profile")
            print("-" * 30)
            print("Available operations when viewing a recipe (requires login)")
            print("- *Bookmark this recipe")
            print("- *Rate this recipe")
        print("*" * 70)
        user_input = input("Select an operation number (type 'q' to exit): ")

        while not user_input.isnumeric() and user_input != 'q':
            user_input = input("Invalid input. Please type a valid operation number (type 'q' to exit): ")


if __name__ == "__main__":
    main()