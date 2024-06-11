import bcrypt
import psycopg2

from database_setup import establish_connection


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

    def get_recommendations(self):
        # 데이터베이스에 연결
        conn = establish_connection()
        if conn is None:
            print("No connection to PostgreSQL!")
            return None
        
        try:
            cur = conn.cursor()

            # 유저가 찜한 및 레이팅 준 레시피들
            user_recipes_query = f"""SELECT recipeID
            FROM recipe.UserInteractions
            WHERE userID = {self.ID};
            """
            
            cur.execute(user_recipes_query)
            user_recipes = [row[0] for row in cur.fetchall()]
        
            if not user_recipes:
                return None

            frequent_itemsets_query = """SELECT recipeB AS recommendedRecipe
            FROM recipe.FrequentPairs
            WHERE recipeA = ANY(%s)
            UNION
            SELECT recipeA AS recommendedRecipe
            FROM recipe.FrequentPairs
            WHERE recipeB = ANY(%s);
            """
            cur.execute(frequent_itemsets_query, (user_recipes, user_recipes))
            recommendations = cur.fetchall()
            
            recommended_recipes = [row[0] for row in recommendations]
        
            # Fetch detailed information about the recommended recipes
            if recommended_recipes:
                detailed_info_query = """
                SELECT recipeID, title, type, description, instructions, avgRating
                FROM recipe.Recipes
                WHERE recipeID = ANY(%s);
                """
                cur.execute(detailed_info_query, (recommended_recipes,))
                detailed_recommendations = cur.fetchall()
            return detailed_recommendations

        except psycopg2.Error as e:
            conn.rollback()
            print("*" * 70)
            print("An error occurred with PostgreSQL")
            print(e)
            return None
        
        finally:
            conn.commit()
            cur.close()
            conn.close()
    
    def create_bookmark(self, recipe_id) -> bool:
        conn = establish_connection()
        if conn is None:
            print("No connection to PostgreSQL!")
            return False
        
        try:
            cursor = conn.cursor()
            
            query = """
            INSERT INTO recipe.Bookmark (userID, recipeID)
            VALUES (%s, %s)
            ON CONFLICT (userID, recipeID) DO NOTHING;
            """

            cursor.execute(query, (self.ID, recipe_id))
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
        
    def add_or_update_rating(self, recipe_id, rating):
        conn = establish_connection()
        if conn is None:
            print("No connection to PostgreSQL!")
            return False
        
        try:
            cursor = conn.cursor()
            
            query = """
            INSERT INTO recipe.Rating (userID, recipeID, rating)
            VALUES (%s, %s, %s)
            ON CONFLICT (userID, recipeID) 
            DO UPDATE SET rating = EXCLUDED.rating, createdAt = CURRENT_TIMESTAMP;
            """
            
            cursor.execute(query, (self.ID, recipe_id, rating))
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
    
    def edit_recipe(self, recipe_title, new_description=None, new_instructions=None, ingredients=None) -> int:
        conn = establish_connection()
        if conn is None:
            print("No connection to PostgreSQL!")
            return False
        
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT recipeID, beingEdited, description, instructions FROM recipe.Recipes WHERE title = %s",
                (recipe_title,)
            )
            result = cur.fetchone()
            
            if not result:
                return -2
            
            recipe_id, being_edited, current_description, current_instructions = result
            
            if being_edited:
                return 0
            
            cur.execute(
                """
                INSERT INTO recipe.RecipeEditQueue (recipeID, editorID, oldDescription, newDescription, oldInstruction, newInstruction)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING editID
                """,
                (recipe_id, self.ID, current_description, new_description, current_instructions, new_instructions)
            )
            edit_id = cur.fetchone()[0]
            
            cur.execute(
                "UPDATE recipe.Recipes SET beingEdited = TRUE WHERE recipeID = %s",
                (recipe_id,)
            )

            if ingredients:
                for ingredient in ingredients:
                    ingredient_name, new_quantity, new_calory = ingredient
                    
                    cur.execute(
                        "SELECT ingredientID FROM recipe.Ingredients WHERE ingredientName = %s",
                        (ingredient_name,)
                    )
                    result = cur.fetchone()
                    
                    if result:
                        ingredient_id = result[0]
                    else:
                        cur.execute(
                            """
                            INSERT INTO recipe.Ingredients (ingredientName, calory)
                            VALUES (%s, %s)
                            RETURNING ingredientID
                            """,
                            (ingredient_name, new_calory)
                        )
                        ingredient_id = cur.fetchone()[0]
                    
                    cur.execute(
                        """
                        INSERT INTO recipe.IngredientEditQueue (editID, recipeID, ingredientID, newQuantity, newIngredientName, newCalory)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (edit_id, recipe_id if result else None, ingredient_id, new_quantity, ingredient_name, new_calory)
                    )
            return 1

        except psycopg2.Error as e:
            conn.rollback()
            print("*" * 70)
            print("An error occurred with PostgreSQL")
            print(e)
            # Commit the transaction
            conn.commit()
            return -1
        
        finally:
            conn.commit()
            cur.close()
            conn.close()

    def retrieve_edit_queue(self):
        conn = establish_connection()
        if conn is None:
            print("No connection to PostgreSQL!")
            return None
        
        try:
            edits = None
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    re.editID, re.recipeID, r.title, re.editorID, re.oldDescription, re.newDescription, 
                    re.oldInstruction, re.newInstruction, ieq.ingredientID, i.ingredientName, 
                    ieq.newQuantity, ieq.newIngredientName, ieq.newCalory
                FROM 
                    recipe.RecipeEditQueue re
                LEFT JOIN 
                    recipe.Recipes r ON re.recipeID = r.recipeID
                LEFT JOIN 
                    recipe.IngredientEditQueue ieq ON re.editID = ieq.editID
                LEFT JOIN 
                    recipe.Ingredients i ON ieq.ingredientID = i.ingredientID
                WHERE 
                    re.isApproved IS NULL
                ORDER BY 
                    re.editTimestamp
            """)
            edits = cur.fetchall()
            return edits

        except psycopg2.Error as e:
            conn.rollback()
            print("*" * 70)
            print("An error occurred with PostgreSQL")
            print(e)
            # Commit the transaction
            conn.commit()
    
        finally:
            conn.commit()
            cur.close()
            conn.close()
        
    def approve_edit_request(self, edit_id: int, approve: bool = True):
        conn = establish_connection()
        if conn is None:
            print("No connection to PostgreSQL!")
            return None
        
        try:
            cursor = conn.cursor()

            # Lock the specific edit request
            lock_request_query = """
            SELECT re.editID, re.recipeID, re.editorID, re.oldDescription, re.newDescription, re.oldInstruction, re.newInstruction
            FROM recipe.RecipeEditQueue re
            WHERE re.editID = %s AND re.isapproved IS NULL
            FOR UPDATE;
            """
            cursor.execute(lock_request_query, (edit_id,))
            request = cursor.fetchone()
            
            if not request:
                return -1
            
            recipe_id = request[1]

            if approve:
                # Update the Recipes table
                update_recipe_query = """
                UPDATE recipe.Recipes
                SET description = %s, instructions = %s, updatedAt = CURRENT_TIMESTAMP, beingEdited = false
                WHERE recipeID = %s;
                """
                cursor.execute(update_recipe_query, (request[4], request[6], recipe_id))

                # Fetch and update associated ingredient edits
                fetch_ingredient_edits_query = """
                SELECT ie.ingredientID, ie.newQuantity, ie.newIngredientName, ie.newCalory
                FROM recipe.IngredientEditQueue ie
                WHERE ie.editID = %s;
                """
                cursor.execute(fetch_ingredient_edits_query, (edit_id,))
                ingredient_edits = cursor.fetchall()

                for ingredient_edit in ingredient_edits:
                    ingredient_id, new_quantity, new_name, new_calory = ingredient_edit

                    if new_name:
                        # Update ingredient name and calory if provided
                        update_ingredient_query = """
                        UPDATE recipe.Ingredients
                        SET ingredientName = %s, calory = %s
                        WHERE ingredientID = %s;
                        """
                        cursor.execute(update_ingredient_query, (new_name, new_calory, ingredient_id))

                    # Update the Recipe_Ingredients table with the new quantity
                    update_recipe_ingredient_query = """
                    UPDATE recipe.Recipe_Ingredients
                    SET quantity = %s
                    WHERE recipeID = %s AND ingredientID = %s;
                    """
                    cursor.execute(update_recipe_ingredient_query, (new_quantity, recipe_id, ingredient_id))
            
            # Update the RecipeEditQueue to reflect the decision
            update_edit_queue_query = """
            UPDATE recipe.RecipeEditQueue
            SET isApproved = %s
            WHERE editID = %s;
            """
            cursor.execute(update_edit_queue_query, (approve, edit_id))

            return 1

        except psycopg2.Error as e:
            conn.rollback()
            print("*" * 70)
            print("An error occurred with PostgreSQL")
            print(e)
            # Commit the transaction
            conn.commit()
            return 0
    
        finally:
            conn.commit()
            cursor.close()
            conn.close()
    
    def get_profile(self):
        conn = establish_connection()
        if conn is None:
            print("No connection to PostgreSQL!")
            return None
        
        try:
            cursor = conn.cursor()
            query = """
            SELECT userID, username, email, firstname, lastname, role, createdAt, updatedAt, bookmark_count, rating_count
            FROM user_profiles
            WHERE userID = %s;
            """
            cursor.execute(query, (self.ID,))
            user_profile = cursor.fetchone()
            if user_profile:
                return {
                    "userID": user_profile[0],
                    "username": user_profile[1],
                    "email": user_profile[2],
                    "firstname": user_profile[3],
                    "lastname": user_profile[4],
                    "role": user_profile[5],
                    "createdAt": user_profile[6],
                    "updatedAt": user_profile[7],
                    "bookmark_count": user_profile[8],
                    "rating_count": user_profile[9]
                }
            else:
                return None

        except psycopg2.Error as e:
            conn.rollback()
            print("*" * 70)
            print("An error occurred with PostgreSQL")
            print(e)
            # Commit the transaction
            conn.commit()
            return None
    
        finally:
            conn.commit()
            cursor.close()
            conn.close()

    def get_bookmarks(self):
        conn = establish_connection()
        if conn is None:
            print("No connection to PostgreSQL!")
            return None
        
        try:
            cursor = conn.cursor()
            query = """
            SELECT recipeID
            FROM recipe.Bookmark
            WHERE userID = %s;
            """
            cursor.execute(query, (self.ID,))
            bookmarks = cursor.fetchall()
            recipe_ids =  [bookmark[0] for bookmark in bookmarks]
        
            if not recipe_ids:
                return None
            
            query = """
            SELECT title, recipeID, type, description, instructions, calory, avgRating
            FROM recipe.Recipes
            WHERE recipeID = ANY(%s);
            """
            cursor.execute(query, (recipe_ids,))
            recipes = cursor.fetchall()
            return recipes

        except psycopg2.Error as e:
            conn.rollback()
            print("*" * 70)
            print("An error occurred with PostgreSQL")
            print(e)
            # Commit the transaction
            conn.commit()
            return None
    
        finally:
            conn.commit()
            cursor.close()
            conn.close()

    def get_ratings(self):
        conn = establish_connection()
        if conn is None:
            print("No connection to PostgreSQL!")
            return None
        
        try:
            cursor = conn.cursor()
            query = """
            SELECT recipeID, rating
            FROM recipe.Rating
            WHERE userID = %s;
            """
            cursor.execute(query, (self.ID,))
            ratings = cursor.fetchall()
        
            if not ratings:
                return None
            
            recipe_ids = [rating[0] for rating in ratings]
            user_ratings_dict = {rating[0]: rating[1] for rating in ratings}

            query = """
            SELECT title, recipeID, type, description, instructions, calory, avgRating
            FROM recipe.Recipes
            WHERE recipeID = ANY(%s);
            """
            cursor.execute(query, (recipe_ids,))
            recipes = cursor.fetchall()
            return recipes

        except psycopg2.Error as e:
            conn.rollback()
            print("*" * 70)
            print("An error occurred with PostgreSQL")
            print(e)
            # Commit the transaction
            conn.commit()
            return None
    
        finally:
            conn.commit()
            cursor.close()
            conn.close()

    def modify_username(self, new_username: str, password: str) -> bool:
        if self.authenticate(password):
            conn = establish_connection()
            if conn is None:
                print("No connection to PostgreSQL!")
                return False
            
            try:
                cursor = conn.cursor()

                # find if duplicate username exists
                cursor.execute(f"SELECT username FROM recipe.Users WHERE username = '{new_username}'")
                user = cursor.fetchone()
                
                # if exists
                if user:
                    print(f"User with '{new_username}' already exists!")
                    return False
                    
                # otherwise, update
                else:
                    cursor.execute(f"UPDATE recipe.Users SET username = '{new_username}' WHERE userID = {self.ID}")
                    self.username = new_username
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
    
    def modify_email(self, new_email: str, password: str) -> bool:
        if self.authenticate(password):
            conn = establish_connection()
            if conn is None:
                print("No connection to PostgreSQL!")
                return False
            
            try:
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
                    return True
                    

            except psycopg2.Error as e:
                conn.rollback()
                print("*" * 70)
                print("An error occurred with PostgreSQL")
                print(e)

            finally:
                conn.commit()
                cursor.close()
                conn.close()

    def modify_password(self, new_password: str, password: str) -> None:
        if self.authenticate(password):
            conn = establish_connection()
            if conn is None:
                print("No connection to PostgreSQL!")
                return False
            
            try:
                cursor = conn.cursor()

                salt = bcrypt.gensalt()

                # hash the password
                new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)

                # change it to string
                new_hashed_password = new_hashed_password.decode('utf-8')

                # update
                cursor.execute(f"UPDATE recipe.Users SET password_hash = '{new_hashed_password}' WHERE userID = {self.ID}")
                self.hashed_password = new_hashed_password
                return True
                    
            except psycopg2.Error as e:
                conn.rollback()
                print(f"An error occurred: {e}")
                return False

            finally:
                conn.commit()
                cursor.close()
                conn.close()
    
    def authenticate(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))