import psycopg2

from database_setup import establish_connection, encode_text

# return recipes information given recipe_id
def get_recipe(recipe_id: int):
    conn = establish_connection()
    if conn is None:
        print("*" * 70)
        print("No connection to PostgreSQL!")
        return None
    
    try:
        cursor = conn.cursor()
        query = f"""
        SELECT 
            r.recipeID,
            r.title,
            r.type,
            r.description,
            r.instructions,
            r.calory,
            r.avgRating,
            r.beingEdited,
            r.createdAt AS recipeCreatedAt,
            r.updatedAt AS recipeUpdatedAt,
            creator.username AS creatorUsername,
            lastEditor.username AS lastEditorUsername,
            i.ingredientName,
            ri.quantity,
            i.calory AS ingredientCalory
        FROM 
            recipe.Recipes r
        LEFT JOIN 
            recipe.Users creator ON r.creatorID = creator.userID
        LEFT JOIN 
            recipe.Users lastEditor ON r.lastUpdatorID = lastEditor.userID
        LEFT JOIN 
            recipe.Recipe_Ingredients ri ON r.recipeID = ri.recipeID
        LEFT JOIN 
            recipe.Ingredients i ON ri.ingredientID = i.ingredientID
        WHERE 
            r.recipeID = {recipe_id};
        """
    
        cursor.execute(query)

        results = cursor.fetchall()
        return results

    except psycopg2.Error as e:
        conn.rollback()
        print("*" * 70)
        print("An error occurred with PostgreSQL")
        print(e)
        return None
    
    finally:
        conn.commit()
        cursor.close()
        conn.close()

# Implements hybrid search for recipe search in scenario 2
def find_similar_recipes(title: str = None, description: str = None, instructions: str = None,
                         recipe_type: str = None, min_calory: int = None, max_calory: int = None,
                         ingredients: list = None, creatorUsername: str = None, num_results: int = 5):
    # Encode the input title, description, and instructions as vectors if provided
    title_vector = encode_text(title) if title else None
    description_vector = encode_text(description) if description else None
    instructions_vector = encode_text(instructions) if instructions else None

    conn = establish_connection()
    if conn is None:
        print("*" * 70)
        print("No connection to PostgreSQL!")
        return None
    
    try:
        cursor = conn.cursor()

        # Base query to find similar recipes
        query_sql = "SELECT DISTINCT r.recipeID, r.title, r.description, r.instructions, r.type, r.calory, r.avgRating"
        
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
        conn.rollback()
        print("*" * 70)
        print("An error occurred with PostgreSQL")
        print(e)
        return None
    
    finally:
        conn.commit()
        cursor.close()
        conn.close()

# Gets materialized view of highest average rated recipes for scenario 3
def get_materialized_view(num: int = 5):
    conn = establish_connection()
    if conn is None:
        print("*" * 70)
        print("No connection to PostgreSQL!")
        return None
    
    try:
        cursor = conn.cursor()
        query = "SELECT title, recipeid, type, description, instructions, calory, avgrating FROM recipe.TopRatedRecipes LIMIT " + str(num)
        cursor.execute(query)
        results = cursor.fetchall()
        return results

    except psycopg2.Error as e:
        conn.rollback()        
        print("*" * 70)
        print("An error occurred with PostgreSQL")
        print(e)
        return None
    
    finally:
        conn.commit()
        cursor.close()
        conn.close()

def get_partitioned_view():
    conn = establish_connection()
    if conn is None:
        print("*" * 70)
        print("No connection to PostgreSQL!")
        return None
    
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT *
            FROM (
                SELECT
                    recipeID,
                    title,
                    type,
                    description,
                    instructions,
                    calory,
                    avgRating,
                    ROW_NUMBER() OVER (PARTITION BY type ORDER BY avgRating DESC NULLS LAST) AS rank
                FROM recipe.Recipes
            ) ranked_recipes
            WHERE rank = 1;
        """

        cursor.execute(query)
        results = cursor.fetchall()
        return results

    except psycopg2.Error as e:
        conn.rollback()        
        print("*" * 70)
        print("An error occurred with PostgreSQL")
        print(e)
        return None
    
    finally:
        conn.commit()
        cursor.close()
        conn.close()

