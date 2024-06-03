import psycopg2

db_config = {
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

def fetch_lowest_calory_recipes():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 각 type별로 calory가 낮은 순으로 1개씩 뽑아오는 쿼리
        query = """
        WITH RankedRecipes AS (
            SELECT
                recipeID,
                title,
                type,
                description,
                instructions,
                calory,
                creatorID,
                lastUpdatorID,
                avgRating,
                beingEdited,
                createdAt,
                updatedAt,
                ROW_NUMBER() OVER (PARTITION BY type ORDER BY calory ASC) AS rn
            FROM
                recipe.Recipes
        )
        SELECT
            recipeID,
            title,
            type,
            description,
            instructions,
            calory,
            creatorID,
            lastUpdatorID,
            avgRating,
            beingEdited,
            createdAt,
            updatedAt
        FROM
            RankedRecipes
        WHERE
            rn = 1;
        """
        cursor.execute(query)
        
        results = cursor.fetchall()
        
        for row in results:
            print(f"Recipe ID: {row[0]}")
            print(f"Title: {row[1]}")
            print(f"Type: {row[2]}")
            print(f"Description: {row[3]}")
            print(f"Instructions: {row[4]}")
            print(f"Calory: {row[5]}")
            print(f"Creator ID: {row[6]}")
            print(f"Last Updator ID: {row[7]}")
            print(f"Average Rating: {row[8]}")
            print(f"Is Being Edited: {row[9]}")
            print(f"Created At: {row[10]}")
            print(f"Updated At: {row[11]}")
            print("-" * 40)
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")