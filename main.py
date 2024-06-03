from database_setup import create_db, initialize_db
import functions

def main():
    create_db()
    initialize_db()

if __name__ == "__main__":
    main()

    # Scenario 8. Partitioning (Recommendation)
    print("Scenario 8. Partitioning : fetch_lowest_calory_recipes")
    functions.fetch_lowest_calory_recipes()