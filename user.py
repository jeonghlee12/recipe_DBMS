import bcrypt
import psycopg2

from database_setup import establish_connection, encode_text


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
            conn = establish_connection()
            if conn is None:
                print("No connection to PostgreSQL!")
                return
            
            try:
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
                    

            except psycopg2.Error as e:
                print(f"An error occurred: {e}")

            finally:
                conn.commit()
                cursor.close()
                conn.close()
    
    def modify_email(self, new_email: str, password: str) -> None:
        if self.authenticate(password):
            conn = establish_connection()
            if conn is None:
                print("No connection to PostgreSQL!")
                return
            
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
                    

            except psycopg2.Error as e:
                print(f"An error occurred: {e}")

            finally:
                conn.commit()
                cursor.close()
                conn.close()

    def modify_password(self, new_password: str, password: str) -> None:
        if self.authenticate(password):
            conn = establish_connection()
            if conn is None:
                print("No connection to PostgreSQL!")
                return
            
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
                    
            except psycopg2.Error as e:
                print(f"An error occurred: {e}")

            finally:
                conn.commit()
                cursor.close()
                conn.close()


    def find_similar_recipes(self, title: str = None, description: str = None, instructions: str = None,
                             recipe_type: str = None, min_calory: int = None, max_calory: int = None,
                             ingredients: list = None, creatorUsername: str = None, num_results: int = 5) -> None:
        # Encode the input title, description, and instructions as vectors if provided
        title_vector = encode_text(title) if title else None
        description_vector = encode_text(description) if description else None
        instructions_vector = encode_text(instructions) if instructions else None
        conn = establish_connection()
        if conn is None:
            return []
        
        try:
            cursor = conn.cursor()
            # Base query to find similar recipes
            query_sql = """
            SELECT DISTINCT r.recipeID, r.title, r.description, r.instructions, r.type, r.calory
            """
            
            params = []
            
            if title_vector:
                query_sql += ", 1 - (r.title_vector <=> %s::vector(384)) AS title_similarity"
                params.append(title_vector)
            else:
                query_sql += ", NULL AS title_similarity"
            
            if description_vector:
                query_sql += ", 1 - (r.description_vector <=> %s::vector(384)) AS description_similarity"
                params.append(description_vector)
            else:
                query_sql += ", NULL AS description_similarity"
            
            if instructions_vector:
                query_sql += ", 1 - (r.instructions_vector <=> %s::vector(384)) AS instructions_similarity"
                params.append(instructions_vector)
            else:
                query_sql += ", NULL AS instructions_similarity"
            
            # Calculate overall similarity based on provided vectors
            similarities = []
            if title_vector:
                similarities.append("1 - (r.title_vector <=> %s::vector(384))")
                params.append(title_vector)
            if description_vector:
                similarities.append("1 - (r.description_vector <=> %s::vector(384))")
                params.append(description_vector)
            if instructions_vector:
                similarities.append("1 - (r.instructions_vector <=> %s::vector(384))")
                params.append(instructions_vector)
            
            if similarities:
                overall_similarity = " + ".join(similarities) + f") / {len(similarities)} AS overall_similarity"
                query_sql += ", (" + overall_similarity
            else:
                query_sql += ", NULL AS overall_similarity"
            
            query_sql += """
            FROM recipe.Recipes r
            LEFT JOIN recipe.Recipe_Ingredients ri ON r.recipeID = ri.recipeID
            LEFT JOIN recipe.Ingredients i ON ri.ingredientID = i.ingredientID
            LEFT JOIN recipe.Users u_creator ON r.creatorID = u_creator.userID
            WHERE TRUE
            """
            
            filters = []
                       
            if recipe_type:
                query_sql += " AND r.type = %s"
                filters.append(recipe_type)
            
            if min_calory is not None:
                query_sql += " AND r.calory >= %s"
                filters.append(min_calory)
            
            if max_calory is not None:
                query_sql += " AND r.calory <= %s"
                filters.append(max_calory)
            
            if ingredients:
                ingredient_conditions = []
                for ingredient in ingredients:
                    ingredient_conditions.append("i.ingredientName = %s")
                    filters.append(ingredient)
                query_sql += " AND (" + " OR ".join(ingredient_conditions) + ")"
            
            if creatorUsername:
                query_sql += " AND u_creator.username = %s"
                filters.append(creatorUsername)
            
            query_sql += " ORDER BY overall_similarity DESC NULLS LAST LIMIT %s"
            filters.append(num_results)
            
            params.extend(filters)
            
            cursor.execute(query_sql, params)
            results = cursor.fetchall()
            return results
        
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            return []
        finally:
            conn.commit()
            cursor.close()
            conn.close()


    #########################################################################################################
    ### Premium and higher role only (no user!)
    #########################################################################################################
    def add_recipe(self, title: str, recipeType: str, description: str, instructions: str, calory: int):
        if (self.role != 'user'):
            title_vector = encode_text(title)
            description_vector = encode_text(description)
            instruction_vector = encode_text(instructions)
            
            conn = establish_connection()
            if conn is None:
                print("No connection to PostgreSQL!")
                return
            
            try:
                cursor = conn.cursor()
                insert_recipe_sql = f"""INSERT INTO recipe.Recipes (title, title_vector, type, description, instructions, description_vector, instructions_vector, calory, creatorID, lastUpdatorID)
                VALUES ('{title}', '{title_vector}', '{recipeType}', '{description}', '{instructions}', '{description_vector}', '{instruction_vector}', '{calory}', '{self.ID}', '{self.ID}')
                """
                cursor.execute(insert_recipe_sql)
                        
            except psycopg2.Error as e:
                print(f"An error occurred: {e}")

            finally:
                conn.commit()
                cursor.close()
                conn.close()

        else:
            print("Regular user privilege does not allow for creating new recipes!")
        