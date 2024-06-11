import os

from user import User
from user_operations import add_user, authenticate_user
from functions import find_similar_recipes, get_materialized_view, get_recipe, get_partitioned_view

########################
# Main user scenario interface functions
#########################

## Scenario 0: create account
def create_account() -> None:
    print("Create an account")
    first = input("First name: ")
    if not first:
        first = input("Please type in a valid name: ")
    last = input("Last name: ")
    if not last:
        last = input("Please type in a valid name: ")
    email = input("Email: ")
    if not email:
        email = input("Please type in a valid email: ")
    username = input("Username: ")
    if not username:
        username = input("Please type in a valid username: ")
    password = input("Password: ")
    if not password:
        password = input("Please type in a valid password: ")
    role = input("Role: ")
    if not role:
        role = input("Please type in a valid role (user, premium, admin): ")

    succ = add_user(firstname=first, lastname=last, email=email, username=username, password=password, role=role)

    print("*" * 70)
    if succ:
        print("Account creation successful!")
    else:
        print("Account creation failed!")
    input("Please press enter to return to main menu....")
    os.system('cls' if os.name == 'nt' else 'clear')

## Scenario 1: login
def login() -> User:
    print("Log in")
    username = input("Username/email: ")
    password = input("Password: ")

    user = authenticate_user(username, password)

    print("*" * 70)
    if user:
        print("Login successful!")
    else:
        print("Login failed!")
    input("Please press enter to return to main menu....")
    os.system('cls' if os.name == 'nt' else 'clear')

    return user

## Scenario 2: recipe search
def recipe_search(user: User):
    print("Please input the relevant information below for the search: if none, please enter again to move on to the next criteria")
    title_desc = input("Title prompt (need not be exact): ")
    desc_desc = input("Description prompt (need not be exact): ")
    instructions_desc = input("Instructions prompt (need not be exact): ")
    recipetype = input("Recipe type (choose from 'Main Course', 'Salad', 'Dessert', 'Appetizer', 'Breakfast', 'Snack'): ")
    min_cal = input("Minimum calorie: ")
    if min_cal != "":
        min_cal = int(min_cal)
    else:
        min_cal = None
    max_cal = input("Maximum calorie: ")
    if max_cal != "":
        max_cal = int(max_cal)
    else:
        max_cal = None
    creator = input("Username of recipe creator: ")
    ingreds = []
    print("Enter ingredients (press Enter without typing anything to stop)")
    user_input = input("Enter ingredient 1: ")
    count = 2
    while user_input != "":
        # Add the input to the list
        ingreds.append(user_input)
        user_input = input("Enter ingredient " + str(count) + ": ")
        count += 1
    top_n = input("How many results show we show: ")
    if top_n != "":
        top_n = int(top_n)
    else:
        top_n = None
    results = find_similar_recipes(title_desc, desc_desc, instructions_desc, recipetype, min_cal, max_cal, ingreds, creator, top_n)
    if results:
        print("*" * 70)
        for row in results:
            print(f"Title: {row[1]}")
            print(f"Recipe ID: {row[0]}")
            print(f"Type: {row[4]}")
            print(f"Description: {row[2]}")
            print(f"Instructions: {row[3]}")
            print(f"Calories: {row[5]}")
            if row[6]:
                print("Average Rating: %.2f" % row[6])
            else: print("Average Rating: N/A")
            print("-" * 50)
        recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
        while recipe_id.isnumeric():
            os.system('cls' if os.name == 'nt' else 'clear')
            recipe_id = int(recipe_id)
            recipe_info = get_recipe(recipe_id)
            if recipe_info:
                # Extract and print recipe details
                recipe_details = recipe_info[0]
                print(f"Recipe ID: {recipe_details[0]}")
                print(f"Title: {recipe_details[1]}")
                print(f"Type: {recipe_details[2]}")
                print(f"Description: {recipe_details[3]}")
                print(f"Instructions: {recipe_details[4]}")
                print(f"Calories: {recipe_details[5]}")
                if recipe_details[6]:
                    print("Average Rating: %.2f" % recipe_details[6])
                else: print("Average Rating: N/A")
                print(f"Created At: {recipe_details[8]}")
                print(f"Updated At: {recipe_details[9]}")
                print(f"Creator Username: {recipe_details[10]}")
                print(f"Last Editor Username: {recipe_details[11]}")
                
                # Print ingredients
                print("\nIngredients:")
                for result in recipe_info:
                    ingredient_name = result[12]
                    quantity = result[13]
                    ingredient_calory = result[14]
                    print(f"  - {ingredient_name}: {quantity} units, {ingredient_calory} calories per unit")
            print("*" * 70)
            if user:
                print("If you want to bookmark this recipe, type 'b'.\nIf you want to rate this recipe, type 'r'.\nIf you want to go back to the recipes list, type 'l'.\nIf you want to return to the main menu, type 'm'.")
                con_input = input("Type here: ")
                print("*" * 40)
                while con_input != 'm' and con_input != 'l':
                    if con_input == 'b':
                        succ = user.create_bookmark(recipe_id)
                    elif con_input == 'r':
                        rating = int(input("Your rating: "))
                        succ = user.add_or_update_rating(recipe_id, rating)
                        print("*" * 40)
                    if succ:
                        if con_input == 'b':
                            print('Bookmark created!')
                        else:
                            print('Rating created!')
                    else:
                        print('Operation failed!')
                        input("Please press enter to return to main menu....")
                        return
                    print("*" * 70)
                    print("If you want to bookmark this recipe, type 'b'.\nIf you want to rate this recipe, type 'r'.\nIf you want to go back to the recipes list, type 'l'.\nIf you want to return to the main menu, type 'm'.")
                    con_input = input("Type here: ")
                    print("*" * 40)
            else:
                con_input = input("If you want to go back to the recipes list, type 'r'. If you want to return to the main menu, type 'm': ")
            if con_input == 'm':
                return
            os.system('cls' if os.name == 'nt' else 'clear')
            print("*" * 70)
            for row in results:
                print(f"Title: {row[1]}")
                print(f"Recipe ID: {row[0]}")
                print(f"Type: {row[4]}")
                print(f"Description: {row[2]}")
                print(f"Instructions: {row[3]}")
                print(f"Calories: {row[5]}")
                if row[6]:
                    print("Average Rating: %.2f" % row[6])
                else: print("Average Rating: N/A")
                print("-" * 50)
            recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
    else:
        print("*" * 70)
        print("Failed to retrieve results! There may be no matching recipes!")
        input("Please press enter to return to main menu....")
    os.system('cls' if os.name == 'nt' else 'clear')

## Scenario 3: get recipe ranking by highest average rating
def get_popular_recipes(user: User) -> None:
    print("These are the top 5 ranking recipes by highest average rating")
    results = get_materialized_view()
    if results:
        print("-" * 50)
        for row in results:
            print(f"Title: {row[0]}")
            print(f"Recipe ID: {row[1]}")
            print(f"Type: {row[2]}")
            print(f"Description: {row[3]}")
            print(f"Instructions: {row[4]}")
            print(f"Calories: {row[5]}")
            if row[6]:
                print("Average Rating: %.2f" % row[6])
            else: print("Average Rating: N/A")
            print("-" * 50)
        recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
        while recipe_id.isnumeric():
            os.system('cls' if os.name == 'nt' else 'clear')
            recipe_id = int(recipe_id)
            recipe_info = get_recipe(recipe_id)
            if recipe_info:
                # Extract and print recipe details
                recipe_details = recipe_info[0]
                print(f"Recipe ID: {recipe_details[0]}")
                print(f"Title: {recipe_details[1]}")
                print(f"Type: {recipe_details[2]}")
                print(f"Description: {recipe_details[3]}")
                print(f"Instructions: {recipe_details[4]}")
                print(f"Calories: {recipe_details[5]}")
                if recipe_details[6]:
                    print("Average Rating: %.2f" % recipe_details[6])
                else: print("Average Rating: N/A")
                print(f"Created At: {recipe_details[8]}")
                print(f"Updated At: {recipe_details[9]}")
                print(f"Creator Username: {recipe_details[10]}")
                print(f"Last Editor Username: {recipe_details[11]}")
                
                # Print ingredients
                print("\nIngredients:")
                for result in recipe_info:
                    ingredient_name = result[12]
                    quantity = result[13]
                    ingredient_calory = result[14]
                    print(f"  - {ingredient_name}: {quantity} units, {ingredient_calory} calories per unit")
            print("*" * 70)
            if user:
                print("If you want to bookmark this recipe, type 'b'.\nIf you want to rate this recipe, type 'r'.\nIf you want to go back to the recipes list, type 'l'.\nIf you want to return to the main menu, type 'm'.")
                con_input = input("Type here: ")
                print("*" * 40)
                while con_input != 'm' and con_input != 'l':
                    if con_input == 'b':
                        succ = user.create_bookmark(recipe_id)
                    elif con_input == 'r':
                        rating = int(input("Your rating: "))
                        succ = user.add_or_update_rating(recipe_id, rating)
                        print("*" * 40)
                    if succ:
                        if con_input == 'b':
                            print('Bookmark created!')
                        else:
                            print('Rating created!')
                    else:
                        print('Operation failed!')
                        input("Please press enter to return to main menu....")
                        return
                    print("*" * 70)
                    print("If you want to bookmark this recipe, type 'b'.\nIf you want to rate this recipe, type 'r'.\nIf you want to go back to the recipes list, type 'l'.\nIf you want to return to the main menu, type 'm'.")
                    con_input = input("Type here: ")
                    print("*" * 40)
            else:
                con_input = input("If you want to go back to the recipes list, type 'r'. If you want to return to the main menu, type 'm': ")
            if con_input == 'm':
                break
            os.system('cls' if os.name == 'nt' else 'clear')
            for row in results:
                print(f"Title: {row[1]}")
                print(f"Recipe ID: {row[0]}")
                print(f"Type: {row[4]}")
                print(f"Description: {row[2]}")
                print(f"Instructions: {row[3]}")
                print(f"Calories: {row[5]}")
                if row[6]:
                    print("Average Rating: %.2f" % row[6])
                else: print("Average Rating: N/A")
                print("-" * 50)
            recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
    else:
        print("*" * 70)
        print("Failed to retrieve results! There may be no matching recipes!")
        input("Please press enter to return to main menu....")
    os.system('cls' if os.name == 'nt' else 'clear')

def get_partitioned_recipes(user: User) -> None:
    print("These are the top ranking recipes for each recipe type by average rating")
    results = get_partitioned_view()
    if results:
        print("-" * 50)
        for row in results:
            print(f"Title: {row[1]}")
            print(f"Recipe ID: {row[0]}")
            print(f"Type: {row[2]}")
            print(f"Description: {row[3]}")
            print(f"Instructions: {row[4]}")
            print(f"Calories: {row[5]}")
            if row[6]:
                print("Average Rating: %.2f" % row[6])
            else: print("Average Rating: N/A")
            print("-" * 50)
        recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
        while recipe_id.isnumeric():
            os.system('cls' if os.name == 'nt' else 'clear')
            recipe_id = int(recipe_id)
            recipe_info = get_recipe(recipe_id)
            if recipe_info:
                # Extract and print recipe details
                recipe_details = recipe_info[0]
                print(f"Recipe ID: {recipe_details[0]}")
                print(f"Title: {recipe_details[1]}")
                print(f"Type: {recipe_details[2]}")
                print(f"Description: {recipe_details[3]}")
                print(f"Instructions: {recipe_details[4]}")
                print(f"Calories: {recipe_details[5]}")
                if recipe_details[6]:
                    print("Average Rating: %.2f" % recipe_details[6])
                else: print("Average Rating: N/A")
                print(f"Created At: {recipe_details[8]}")
                print(f"Updated At: {recipe_details[9]}")
                print(f"Creator Username: {recipe_details[10]}")
                print(f"Last Editor Username: {recipe_details[11]}")
                
                # Print ingredients
                print("\nIngredients:")
                for result in recipe_info:
                    ingredient_name = result[12]
                    quantity = result[13]
                    ingredient_calory = result[14]
                    print(f"  - {ingredient_name}: {quantity} units, {ingredient_calory} calories per unit")
            print("*" * 70)
            if user:
                print("If you want to bookmark this recipe, type 'b'.\nIf you want to rate this recipe, type 'r'.\nIf you want to go back to the recipes list, type 'l'.\nIf you want to return to the main menu, type 'm'.")
                con_input = input("Type here: ")
                print("*" * 40)
                while con_input != 'm' and con_input != 'l':
                    if con_input == 'b':
                        succ = user.create_bookmark(recipe_id)
                    elif con_input == 'r':
                        rating = int(input("Your rating: "))
                        succ = user.add_or_update_rating(recipe_id, rating)
                        print("*" * 40)
                    if succ:
                        if con_input == 'b':
                            print('Bookmark created!')
                        else:
                            print('Rating created!')
                    else:
                        print('Operation failed!')
                        input("Please press enter to return to main menu....")
                        return
                    print("*" * 70)
                    print("If you want to bookmark this recipe, type 'b'.\nIf you want to rate this recipe, type 'r'.\nIf you want to go back to the recipes list, type 'l'.\nIf you want to return to the main menu, type 'm'.")
                    con_input = input("Type here: ")
                    print("*" * 40)
            else:
                con_input = input("If you want to go back to the recipes list, type 'r'. If you want to return to the main menu, type 'm': ")
            if con_input == 'm':
                break
            os.system('cls' if os.name == 'nt' else 'clear')
            for row in results:
                print(f"Title: {row[1]}")
                print(f"Recipe ID: {row[0]}")
                print(f"Type: {row[4]}")
                print(f"Description: {row[2]}")
                print(f"Instructions: {row[3]}")
                print(f"Calories: {row[5]}")
                if row[6]:
                    print("Average Rating: %.2f" % row[6])
                else: print("Average Rating: N/A")
                print("-" * 50)
            recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
    else:
        print("*" * 70)
        print("Failed to retrieve results! There may be no matching recipes!")
        input("Please press enter to return to main menu....")
    os.system('cls' if os.name == 'nt' else 'clear')

## Scenario 6: recipe recommendations
def get_recommended_recipe(user: User) -> None:
    if not user:
        print('Please log in first to view your profile!')
        input("Please press enter to return to main menu....")
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    print(f"Recommended recipes for {user.firstname}")
    recs = user.get_recommendations()
    if recs:
        for row in recs:
            print(f"Title: {row[1]}")
            print(f"Recipe ID: {row[0]}")
            print(f"Type: {row[2]}")
            print(f"Description: {row[3]}")
            print(f"Instructions: {row[4]}")
            if row[5]:
                print("Average Rating: %.2f" % row[5])
            else: print("Average Rating: N/A")
            print("-" * 50)
        recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
        while recipe_id.isnumeric():
            os.system('cls' if os.name == 'nt' else 'clear')
            recipe_id = int(recipe_id)
            recipe_info = get_recipe(recipe_id)
            if recipe_info:
                # Extract and print recipe details
                recipe_details = recipe_info[0]
                print(f"Recipe ID: {recipe_details[0]}")
                print(f"Title: {recipe_details[1]}")
                print(f"Type: {recipe_details[2]}")
                print(f"Description: {recipe_details[3]}")
                print(f"Instructions: {recipe_details[4]}")
                print(f"Calories: {recipe_details[5]}")
                if recipe_details[6]:
                    print("Average Rating: %.2f" % recipe_details[6])
                else: print("Average Rating: N/A")
                print(f"Created At: {recipe_details[8]}")
                print(f"Updated At: {recipe_details[9]}")
                print(f"Creator Username: {recipe_details[10]}")
                print(f"Last Editor Username: {recipe_details[11]}")
                
                # Print ingredients
                print("\nIngredients:")
                for result in recipe_info:
                    ingredient_name = result[12]
                    quantity = result[13]
                    ingredient_calory = result[14]
                    print(f"  - {ingredient_name}: {quantity} units, {ingredient_calory} calories per unit")
            print("-" * 40)
            print("If you want to bookmark this recipe, type 'b'.\nIf you want to rate this recipe, type 'r'.\nIf you want to go back to the recipes list, type 'l'.\nIf you want to return to the main menu, type 'm'.")
            con_input = input("Type here: ")
            print("-"*40)
            while con_input != 'm' and con_input != 'l':
                if con_input == 'b':
                    succ = user.create_bookmark(recipe_id)
                elif con_input == 'r':
                    rating = int(input("Your rating: "))
                    succ = user.add_or_update_rating(recipe_id, rating)
                if succ:
                    print('Operation was successful!')
                else:
                    print('Operation failed!')
                    print("-"*40)
                print("If you want to bookmark this recipe, type 'b'.\nIf you want to rate this recipe, type 'r'.\nIf you want to go back to the recipes list, type 'l'.\nIf you want to return to the main menu, type 'm'.")
                con_input = input("Type here: ")
                print("-"*40)
            if con_input == 'm':
                break
            os.system('cls' if os.name == 'nt' else 'clear')
            for row in recs:
                print(f"Title: {row[1]}")
                print(f"Recipe ID: {row[0]}")
                print(f"Type: {row[2]}")
                print(f"Description: {row[3]}")
                print(f"Instructions: {row[4]}")
                if row[5]:
                    print("Average Rating: %.2f" % row[5])
                else: print("Average Rating: N/A")
                print("-" * 50)
            recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
    else:
        print("*" * 70)
        print("Failed to retrieve recommendations!")
        input("Please press enter to return to main menu....")
    os.system('cls' if os.name == 'nt' else 'clear')

## Scenario 7: recipe edit/create
def edit_recipe(user: User) -> None:
    if not user:
        print('Please log in first to view your profile!')
        input("Please press enter to return to main menu....")
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    if user.role == 'user':
        print('You do not have recipe edit access!')
        input("Please press enter to return to main menu....")
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    
    print("Edit a recipe")
    print("All edit attempts will need adminstrator approval before being commited.")
    print("Press enter once more if no changes are required for the category")
    print("*" * 50)
    title = input("Title of recipe you want to edit/create: ")
    new_desc = input("New description: ")
    new_inst = input("New instruction: ")
    new_ingreds = []
    print("Enter ingredients to change in 'name, quantity, calory' format (press Enter without typing anything to stop)")
    user_input = input("Enter ingredient 1: ")
    count = 2
    while user_input != "":
        # Add the input to the list
        ingred_triple = user_input.split(",")
        new_ingreds.append(([trip.strip() for trip in ingred_triple]))
        user_input = input("Enter ingredient " + str(count) + ": ")
        count += 1
    
    if not title and not new_desc and not new_inst and not new_ingreds:
        print("No changes made...")
    else:
        succ = user.edit_recipe(title, new_desc, new_inst, new_ingreds)

    print("*" * 70)
    if succ == 1:
        print("Request successfully submitted!")
    elif succ == -2:
        print("Recipe doesn't exist!")
    elif succ == 0:
        print("Recipe currently has a request already! Try again later.")
    else:
        print("Request failed!")
    input("Please press enter to return to main menu....")
    os.system('cls' if os.name == 'nt' else 'clear')

## Scenario 8: Approve edits:
def approve_recipe_edit(user: User) -> None:
    if not user:
        print('Please log in first to view your profile!')
        input("Please press enter to return to main menu....")
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    if user.role != 'admin':
        print('You do not have recipe edit approval access!')
        input("Please press enter to return to main menu....")
        os.system('cls' if os.name == 'nt' else 'clear')
        return

    print("These are the current edit requests")
    edits = user.retrieve_edit_queue()
    if not edits:
        print('Something went wrong!')
        input("Please press enter to return to main menu....")
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    
    for edit in edits:
        (edit_id, recipe_id, title, editor_id, old_description, new_description, 
         old_instruction, new_instruction, ingredient_id, ingredient_name, 
         new_quantity, new_ingredient_name, new_calory) = edit
        
        print(f"Edit ID: {edit_id}")
        print(f"Recipe ID: {recipe_id}")
        print(f"Recipe Title: {title}")
        print(f"Editor ID: {editor_id}")
        print("Description:")
        print(f"  Old: {old_description}")
        print(f"  New: {new_description}")
        print("Instructions:")
        print(f"  Old: {old_instruction}")
        print(f"  New: {new_instruction}")
        
        if ingredient_id:
            print("Ingredient Changes:")
            print(f"  Ingredient ID: {ingredient_id}")
            print(f"  Ingredient Name: {ingredient_name}")
            print(f"  New Quantity: {new_quantity}")
            print(f"  New Ingredient Name: {new_ingredient_name}")
            print(f"  New Calorie: {new_calory}")
        print("*" * 50)
    edit_num = int(input("Select an edit request by edit_id to approve or disapprove: "))
    approval = input("Do you approve this request (Y\\N): ")
    if approval == 'N':
        succ = user.approve_edit_request(edit_num, False)
    else:
        succ = user.approve_edit_request(edit_num)

    print("*" * 70)
    if succ == -1:
        print("Invalid edit ID!")
    elif succ == 1:
        if approval == 'Y':
            print("Request successfully approved!")
        else:
            print("Request successfully declined!")
    else:
        if approval == 'Y':
            print("Failed to approve request!")
        else:
            print("Failed to decline request!")
    input("Please press enter to return to main menu....")
    os.system('cls' if os.name == 'nt' else 'clear')

## Scenario 9: view profile
def view_profile(user: User) -> None:
    if not user:
        print('Please log in first to view your profile!')
        input("Please press enter to return to main menu....")
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    profile = user.get_profile()
    if profile:
        print(f"Profile for {profile['firstname']} {profile['lastname']}")
        print(f"Level: {profile['role']}")
        print("-" * 40)
        print(f"Email: {profile['email']}")
        print(f"Username: {profile['username']}")
        print(f"Accounted created at: {profile['createdAt']}")
        print(f"Accounted last updated at: {profile['updatedAt']}")
        print("-" * 40)
        print(f"Number of bookmarks: {profile['bookmark_count']}")
        print(f"Number of recipes rated: {profile['rating_count']}")
        print("*" * 70)
        user_input = input("Type 'b' to access bookmarks, 'r' to access ratings, and 'm' to return to main menu: ")
        while user_input != 'm':
            if user_input == 'b':
                results = user.get_bookmarks()
                if results:
                    print("-" * 50)
                    for row in results:
                        print(f"Title: {row[0]}")
                        print(f"Recipe ID: {row[1]}")
                        print(f"Type: {row[2]}")
                        print(f"Description: {row[3]}")
                        print(f"Instructions: {row[4]}")
                        print(f"Calories: {row[5]}")
                        if row[6]:
                            print("Average Rating: %.2f" % row[6])
                        else: print("Average Rating: N/A")
                        print("-" * 50)
                    recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
                    while recipe_id.isnumeric():
                        os.system('cls' if os.name == 'nt' else 'clear')
                        recipe_id = int(recipe_id)
                        recipe_info = get_recipe(recipe_id)
                        if recipe_info:
                            # Extract and print recipe details
                            recipe_details = recipe_info[0]
                            print(f"Recipe ID: {recipe_details[0]}")
                            print(f"Title: {recipe_details[1]}")
                            print(f"Type: {recipe_details[2]}")
                            print(f"Description: {recipe_details[3]}")
                            print(f"Instructions: {recipe_details[4]}")
                            print(f"Calories: {recipe_details[5]}")
                            if recipe_details[6]:
                                print("Average Rating: %.2f" % recipe_details[6])
                            else: print("Average Rating: N/A")
                            print(f"Created At: {recipe_details[8]}")
                            print(f"Updated At: {recipe_details[9]}")
                            print(f"Creator Username: {recipe_details[10]}")
                            print(f"Last Editor Username: {recipe_details[11]}")
                            
                            # Print ingredients
                            print("\nIngredients:")
                            for result in recipe_info:
                                ingredient_name = result[12]
                                quantity = result[13]
                                ingredient_calory = result[14]
                                print(f"  - {ingredient_name}: {quantity} units, {ingredient_calory} calories per unit")
                        print("*" * 70)
                        con_input = input("If you want to go back to the recipes list, type 'r'. If you want to return to the main menu, type 'm': ")
                        if con_input == 'm':
                            user_input = 'm'
                            break
                        os.system('cls' if os.name == 'nt' else 'clear')
                        for row in results:
                            print(f"Title: {row[1]}")
                            print(f"Recipe ID: {row[0]}")
                            print(f"Type: {row[4]}")
                            print(f"Description: {row[2]}")
                            print(f"Instructions: {row[3]}")
                            print(f"Calories: {row[5]}")
                            if row[6]:
                                print("Average Rating: %.2f" % row[6])
                            else: print("Average Rating: N/A")
                            print("-" * 50)
                        recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
                        if recipe_id == 'm':
                            user_input = 'm'
                else:
                    print("You have no bookmarks!")
                    input("Please press enter to return to main menu....")
            if user_input == 'r':
                results = user.get_ratings()
                if results:
                    print("-" * 50)
                    for row in results:
                        print(f"Title: {row[0]}")
                        print(f"Recipe ID: {row[1]}")
                        print(f"Type: {row[2]}")
                        print(f"Description: {row[3]}")
                        print(f"Instructions: {row[4]}")
                        print(f"Calories: {row[5]}")
                        if row[6]:
                            print("Average Rating: %.2f" % row[6])
                        else: print("Average Rating: N/A")
                        print("-" * 50)
                    recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
                    while recipe_id.isnumeric():
                        os.system('cls' if os.name == 'nt' else 'clear')
                        recipe_id = int(recipe_id)
                        recipe_info = get_recipe(recipe_id)
                        if recipe_info:
                            # Extract and print recipe details
                            recipe_details = recipe_info[0]
                            print(f"Recipe ID: {recipe_details[0]}")
                            print(f"Title: {recipe_details[1]}")
                            print(f"Type: {recipe_details[2]}")
                            print(f"Description: {recipe_details[3]}")
                            print(f"Instructions: {recipe_details[4]}")
                            print(f"Calories: {recipe_details[5]}")
                            if recipe_details[6]:
                                print("Average Rating: %.2f" % recipe_details[6])
                            else: print("Average Rating: N/A")
                            print(f"Created At: {recipe_details[8]}")
                            print(f"Updated At: {recipe_details[9]}")
                            print(f"Creator Username: {recipe_details[10]}")
                            print(f"Last Editor Username: {recipe_details[11]}")
                            
                            # Print ingredients
                            print("\nIngredients:")
                            for result in recipe_info:
                                ingredient_name = result[12]
                                quantity = result[13]
                                ingredient_calory = result[14]
                                print(f"  - {ingredient_name}: {quantity} units, {ingredient_calory} calories per unit")
                        print("*" * 70)
                        con_input = input("If you want to go back to the recipes list, type 'r'. If you want to return to the main menu, type 'm': ")
                        if con_input == 'm':
                            user_input = 'm'
                            break
                        os.system('cls' if os.name == 'nt' else 'clear')
                        for row in results:
                            print(f"Title: {row[1]}")
                            print(f"Recipe ID: {row[0]}")
                            print(f"Type: {row[4]}")
                            print(f"Description: {row[2]}")
                            print(f"Instructions: {row[3]}")
                            print(f"Calories: {row[5]}")
                            if row[6]:
                                print("Average Rating: %.2f" % row[6])
                            else: print("Average Rating: N/A")
                            print("-" * 50)
                        recipe_id = input("If you want to select a recipe, enter its ID. If you want to return to the main menu, type 'm': ")
                        if recipe_id == 'm':
                            user_input = 'm'
                else:
                    print("You have no ratings!")
                    input("Please press enter to return to main menu....")
    os.system('cls' if os.name == 'nt' else 'clear')

## Scenario 10: change profile
def change_profile(user: User) -> None:
    if not user:
        print('Please log in first to view your profile!')
        input("Please press enter to return to main menu....")
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    print("Change your profile")
    print("1. username")
    print("2. email")
    print("3. password")
    num = int(input("Select the item you wish to change: "))
    password = input("Please type your password again: ")
    if num == 1:
        new = input("Your new username: ")
        succ = user.modify_username(new, password)
    elif num == 2:
        new = input("Your new email: ")
        succ = user.modify_email(new, password)
    elif num == 3:
        new = input("Your new password: ")
        succ = user.modify_password(new, password)
    print("*" * 70)
    if succ:
        print("Update successful!")
    else:
        print("Update failed!")
    input("Please press enter to return to main menu....")
    os.system('cls' if os.name == 'nt' else 'clear')