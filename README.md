SNU 2024 Spring BKMS 1 Term Project

Authors: Jeong Hyun Lee, 임병희, 손민규, 조언걸

Please run `setup.sh` first to check and install all required packages to run this application.

Run `python main.py` on your terminal console to start the application.


---
- `main.py`: main application - creates and initializes database with functions from `database_setup.py` and calls upon various user case scenarios from `scenarios.py`.
- `database_setup.py`: creates database schema, table, views, materialized views, triggers, indices, etc for the database and also intializes the database with sample data from `setup_db.md`.
- `scenarios.py`: Contains the various scenario functions with terminal interface. Each scenario calls upon relevant functions regarding user creation in `user_operations.py`, common functions from `functions.py` and user specific functions from `user.py`.
- `user_operations.py`: Contains various functions regarding user creation and authentication.
- `functions.py`: Contains common functions such as recipe search, view highest average rated recipes, that don't depend on user login.
- `user.py`: Contains the user class and user dependent functions. For example, getting recommendation differs user by user, and also recipe edits must be made with specific user privileges. Hence, in the user class, functions for getting recommendations, editing recipes, approving recipes, viewing profile, editing profile, etc, are given.
