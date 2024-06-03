from database_setup import create_db, initialize_db
from user_operations import authenticate_user
from initialize_db import initialize
import functions

def main():
    create_db()
    initialize()
    # initialize_db()
    # scenario8()
    testScenario()

def scenario8():
    # Scenario 8. Partitioning (Recommendation)
    print("Scenario 8. Partitioning : fetch_lowest_calory_recipes")
    functions.fetch_lowest_calory_recipes()

def testScenario():
    user1 = authenticate_user('david_lee', 'hashed_password_9')
    result = user1.find_similar_recipes(description="a classic sandwich", min_calory=300, max_calory=550, num_results=3)
    print("Finding similar recipes with similar description to 'classic' with a calories count between 300 and 550 - showing top 3 results")
    for item in result:
        print("---------------------------")
        print("Title:", item[1])
        print("Description:", item[2])
        print("Instructions:", item[3])
        print("Type:", item[4])
        print("Calories:", item[5])


if __name__ == "__main__":
    main()