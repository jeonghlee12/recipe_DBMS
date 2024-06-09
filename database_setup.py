import psycopg2
from transformers import AutoTokenizer, AutoModel
import torch
import bcrypt

# load sentence to token tokenizer model from transformers package
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L12-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L12-v2')

def encode_text(text: str) -> list:
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy().flatten().tolist()

def establish_connection():
    try:
        conn = psycopg2.connect(
            database="postgres",
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
        return conn
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error establishing connection to database: {e}")
        return None


def create_db() -> None:
    conn = establish_connection()

    if conn is None:
        print("No connection to PostgreSQL!")
        return

    cursor = conn.cursor()

    # Drop recipe schema if already exists.
    cursor.execute("DROP SCHEMA IF EXISTS recipe CASCADE")

    # Create schema
    create_schema_sql = "CREATE SCHEMA recipe;"
    cursor.execute(create_schema_sql)

    # Check if pgvector extension exists in PostgreSQL
    check_pgvector_sql = "CREATE EXTENSION IF NOT EXISTS vector;"
    cursor.execute(check_pgvector_sql)
    
    # Create tables
    create_table_sql ='''CREATE TABLE recipe.Users
    (
        userID SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE CHECK (email LIKE '%@%'),
        password_hash VARCHAR(255) NOT NULL,
        firstname VARCHAR(50),
        lastname VARCHAR(50),
        role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'premium', 'admin')),
        createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE recipe.Recipes
    (
        recipeID SERIAL PRIMARY KEY,
        title VARCHAR(50),
        title_vector vector(384),
        type VARCHAR(50),
        description TEXT,
        instructions TEXT,
        description_vector vector(384),
        instructions_vector vector(384),
        calory INTEGER,
        creatorID INTEGER NOT NULL,
        lastUpdatorID INTEGER,
        avgRating DECIMAL DEFAULT NULL CHECK (avgRating >= 0 AND avgRating <= 10),
        beingEdited BOOL DEFAULT FALSE,
        createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (creatorID) REFERENCES recipe.Users(userID),
        FOREIGN KEY (lastUpdatorID) REFERENCES recipe.Users(userID)
    );

    CREATE TABLE recipe.Ingredients
    (
        ingredientID SERIAL PRIMARY KEY,
        ingredientName VARCHAR(50) NOT NULL UNIQUE,
        calory INTEGER
    );

    CREATE TABLE recipe.Recipe_Ingredients
    (
        recipeID INTEGER NOT NULL,
        ingredientID INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        PRIMARY KEY (recipeID, ingredientID),
        FOREIGN KEY (recipeID) REFERENCES recipe.Recipes(recipeID),
        FOREIGN KEY (ingredientID) REFERENCES recipe.Ingredients(ingredientID)
    );

    CREATE TABLE recipe.RecipeEditQueue
    (
        editID SERIAL PRIMARY KEY,
        recipeID INTEGER NOT NULL,
        editorID INTEGER NOT NULL,
        editTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        oldDescription TEXT,
        newDescription TEXT,
        oldInstruction TEXT,
        newInstruction TEXT,
        isApproved BOOL,
        FOREIGN KEY (editorID) REFERENCES recipe.Users(userID),
        FOREIGN KEY (recipeID) REFERENCES recipe.Recipes(recipeID)
    );

    CREATE TABLE recipe.IngredientEditQueue
    (
        editID INTEGER NOT NULL,
        recipeID INTEGER NOT NULL,
        ingredientID INTEGER NOT NULL,
        newQuantity INTEGER NOT NULL,
        newIngredientName VARCHAR(50),
        newCalory INTEGER,
        PRIMARY KEY (editID, recipeID, ingredientID),
        FOREIGN KEY (editID) REFERENCES recipe.RecipeEditQueue(editID),
        FOREIGN KEY (recipeID) REFERENCES recipe.Recipes(recipeID),
        FOREIGN KEY (ingredientID) REFERENCES recipe.Ingredients(ingredientID)
    );

    CREATE TABLE recipe.Bookmark
    (
        bookmarkID SERIAL PRIMARY KEY,
        userID INTEGER NOT NULL,
        recipeID INTEGER NOT NULL,
        UNIQUE (userID, recipeID),
        FOREIGN KEY (userID) REFERENCES recipe.Users(userID),
        FOREIGN KEY (recipeID) REFERENCES recipe.Recipes(recipeID)
    );

    CREATE TABLE recipe.Rating
    (
        ratingID SERIAL PRIMARY KEY,
        userID INTEGER NOT NULL,
        recipeID INTEGER NOT NULL,
        rating NUMERIC NOT NULL CHECK (rating >= 0 AND rating <= 10),
        createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (userID, recipeID),
        FOREIGN KEY (userID) REFERENCES recipe.Users(userID),
        FOREIGN KEY (recipeID) REFERENCES recipe.Recipes(recipeID)
    );
    '''
    cursor.execute(create_table_sql)

    # Create triggers for updating timestamp
    time_triggers_sql = """CREATE OR REPLACE FUNCTION upd_timestamp() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS
    $$
    BEGIN
        IF (NEW != OLD) THEN
            NEW.updatedAt = CURRENT_TIMESTAMP;
            RETURN NEW;
        END IF;
        RETURN OLD;
    END;
    $$;

    CREATE TRIGGER update_user BEFORE UPDATE ON recipe.Users
        FOR EACH ROW EXECUTE FUNCTION upd_timestamp();

    CREATE TRIGGER update_recipes BEFORE UPDATE ON recipe.Recipes
        FOR EACH ROW EXECUTE FUNCTION upd_timestamp();  
    """
    cursor.execute(time_triggers_sql)

    # Create materialized view for top rated recipes and triggers for updating ratings
    mat_view_sql = """CREATE MATERIALIZED VIEW recipe.TopRatedRecipes AS
    SELECT * FROM recipe.Recipes
    ORDER BY avgRating DESC NULLS LAST
    WITH NO DATA;

    REFRESH MATERIALIZED VIEW recipe.TopRatedRecipes;

    CREATE OR REPLACE FUNCTION update_avg_rating_and_refresh_view()
    RETURNS TRIGGER LANGUAGE plpgsql AS $$
    BEGIN
        UPDATE recipe.Recipes
        SET avgRating = (
            SELECT AVG(rating)
            FROM recipe.Rating
            WHERE recipeID = NEW.recipeID
        )
        WHERE recipeID = NEW.recipeID;

        REFRESH MATERIALIZED VIEW recipe.TopRatedRecipes;

        RETURN NEW;
    END;
    $$;

    CREATE TRIGGER trigger_update_avg_rating_and_refresh_view AFTER INSERT OR UPDATE ON recipe.Rating
        FOR EACH ROW EXECUTE FUNCTION update_avg_rating_and_refresh_view();
    """
    cursor.execute(mat_view_sql)

    # create views
    create_views_sql = """
    CREATE OR REPLACE VIEW user_profiles AS
    SELECT 
        u.userID,
        u.username,
        u.email,
        u.firstname,
        u.lastname,
        u.role,
        u.createdAt,
        u.updatedAt,
        (SELECT COUNT(*) FROM recipe.Bookmark b WHERE b.userID = u.userID) AS bookmark_count,
        (SELECT COUNT(*) FROM recipe.Rating r WHERE r.userID = u.userID) AS rating_count
    FROM 
        recipe.Users u;

    CREATE OR REPLACE VIEW recipe.UserInteractions AS
        SELECT userID, recipeID
        FROM recipe.Rating
        UNION
        SELECT userID, recipeID
        FROM recipe.Bookmark;

    CREATE OR REPLACE VIEW recipe.FrequentPairs AS
    WITH RecipePairs AS (
        SELECT
            ui1.recipeID AS recipeA,
            ui2.recipeID AS recipeB,
            COUNT(*) AS support
        FROM
            recipe.UserInteractions ui1
        JOIN
            recipe.UserInteractions ui2
        ON
            ui1.userID = ui2.userID
            AND ui1.recipeID < ui2.recipeID
        GROUP BY
            ui1.recipeID, ui2.recipeID
    )
    SELECT recipeA, recipeB, support
    FROM RecipePairs
    WHERE support >= 2;
    """
    cursor.execute(create_views_sql)
    
    # create indices for optimized search
    create_indices_sql = """
        CREATE INDEX idx_recipes_recipeID ON recipe.Recipes(recipeID);
        CREATE INDEX idx_recipes_creatorID ON recipe.Recipes(creatorID);
        CREATE INDEX idx_recipes_lastUpdatorID ON recipe.Recipes(lastUpdatorID);
        CREATE INDEX idx_recipe_ingredients_recipeID ON recipe.Recipe_Ingredients(recipeID);
        CREATE INDEX idx_recipe_ingredients_ingredientID ON recipe.Recipe_Ingredients(ingredientID);
        CREATE INDEX idx_ingredientName ON recipe.Ingredients(ingredientName);
        CREATE INDEX idx_userID_bookmark ON recipe.Bookmark(userID);
        CREATE INDEX idx_userID_rating ON recipe.Rating(userID);
        CREATE INDEX idx_title_vector ON recipe.Recipes USING ivfflat (title_vector);
        CREATE INDEX idx_description_vector ON recipe.Recipes USING ivfflat (description_vector);
        CREATE INDEX idx_instructions_vector ON recipe.Recipes USING ivfflat (instructions_vector);
        """
    cursor.execute(create_indices_sql)

    conn.commit()
    conn.close()

def initialize_db():
    # Fill tables
    names_list = [
        ('john_doe', 'john@example.com', 'hashed_password_1', 'John', 'Doe', 'user'),
        ('jane_smith', 'jane@example.com', 'hashed_password_2', 'Jane', 'Smith', 'admin'),
        ('mike_jones', 'mike@example.com', 'hashed_password_3', 'Mike', 'Jones', 'premium'),
        ('anna_brown', 'anna@example.com', 'hashed_password_4', 'Anna', 'Brown', 'user'),
        ('chris_white', 'chris@example.com', 'hashed_password_5', 'Chris', 'White', 'premium'),
        ('kate_green', 'kate@example.com', 'hashed_password_6', 'Kate', 'Green', 'user'),
        ('tom_clark', 'tom@example.com', 'hashed_password_7', 'Tom', 'Clark', 'user'),
        ('lucy_adams', 'lucy@example.com', 'hashed_password_8', 'Lucy', 'Adams', 'user'),
        ('david_lee', 'david@example.com', 'hashed_password_9', 'David', 'Lee', 'premium'),
        ('sara_hall', 'sara@example.com', 'hashed_password_10', 'Sara', 'Hall', 'admin')
    ]

    recipe_list = [
        ('Spaghetti Bolognese', 'Main Course', 'A classic Italian pasta dish', '1. Cook the pasta. 2. Prepare the sauce. 3. Mix and serve.', 600, 1),
        ('Chicken Caesar Salad', 'Salad', 'A healthy Caesar salad with grilled chicken', '1. Grill the chicken. 2. Prepare the salad. 3. Mix and serve.', 350, 2),
        ('Chocolate Cake', 'Dessert', 'A rich and moist chocolate cake', '1. Prepare the batter. 2. Bake the cake. 3. Let it cool and serve.', 450, 1),
        ('Vegetable Stir Fry', 'Main Course', 'A quick and easy vegetable stir fry', '1. Prepare the vegetables. 2. Stir fry the vegetables. 3. Serve with rice.', 300, 3),
        ('Pancakes', 'Breakfast', 'Fluffy pancakes perfect for breakfast', '1. Prepare the batter. 2. Cook the pancakes. 3. Serve with syrup.', 400, 1),
        ('Beef Tacos', 'Main Course', 'Spicy beef tacos with salsa', '1. Prepare the beef. 2. Warm the tortillas. 3. Assemble the tacos and serve.', 500, 4),
        ('Lemon Tart', 'Dessert', 'A zesty lemon tart with a crispy crust', '1. Prepare the crust. 2. Make the lemon filling. 3. Bake and serve.', 350, 5),
        ('Minestrone Soup', 'Appetizer', 'A hearty vegetable and pasta soup', '1. Prepare the vegetables. 2. Cook the soup. 3. Serve hot.', 200, 6),
        ('French Toast', 'Breakfast', 'Classic French toast with maple syrup', '1. Prepare the egg mixture. 2. Cook the bread slices. 3. Serve with syrup.', 450, 7),
        ('Greek Salad', 'Salad', 'A refreshing salad with feta cheese and olives', '1. Prepare the vegetables. 2. Mix the dressing. 3. Toss and serve.', 250, 8),
        ('Grilled Cheese Sandwich', 'Snack', 'A simple and delicious grilled cheese sandwich', '1. Butter the bread. 2. Add cheese. 3. Grill until golden brown.', 350, 9),
        ('Apple Pie', 'Dessert', 'A classic apple pie with a flaky crust', '1. Prepare the crust. 2. Make the apple filling. 3. Bake and serve.', 400, 10),
        ('Roast Chicken', 'Main Course', 'Juicy roast chicken with herbs', '1. Prepare the chicken. 2. Roast in the oven. 3. Serve with vegetables.', 600, 3),
        ('Fish and Chips', 'Main Course', 'Crispy fish with golden fries', '1. Prepare the fish. 2. Fry the fish and potatoes. 3. Serve with tartar sauce.', 700, 4),
        ('Caesar Salad', 'Salad', 'Classic Caesar salad with homemade dressing', '1. Prepare the dressing. 2. Toss the salad. 3. Serve with croutons.', 300, 5),
        ('Pumpkin Soup', 'Appetizer', 'Creamy pumpkin soup with a hint of spice', '1. Prepare the pumpkin. 2. Cook the soup. 3. Serve hot.', 150, 6),
        ('Scrambled Eggs', 'Breakfast', 'Fluffy scrambled eggs', '1. Beat the eggs. 2. Cook in a pan. 3. Serve hot.', 250, 7),
        ('Caprese Salad', 'Salad', 'Fresh salad with tomatoes, mozzarella, and basil', '1. Slice the tomatoes and cheese. 2. Arrange on a plate. 3. Drizzle with olive oil and serve.', 200, 8),
        ('Banana Bread', 'Dessert', 'Moist banana bread with walnuts', '1. Prepare the batter. 2. Bake in the oven. 3. Let it cool and serve.', 350, 9),
        ('Chicken Noodle Soup', 'Main Course', 'Comforting chicken noodle soup', '1. Prepare the broth. 2. Add chicken and noodles. 3. Serve hot.', 300, 10)
    ]

    with open('setup_db.md', 'r') as file:
        db_setup = file.read()

    db_setup = db_setup.split(';')
    db_setup = [q.strip() for q in db_setup if q.strip()]

    conn = establish_connection()
    if conn is None:
        print("No connection to PostgreSQL!")
        return
    
    try:
        cursor = conn.cursor()

        salt = bcrypt.gensalt()

        insert_user_sql = "INSERT INTO recipe.Users (username, email, password_hash, firstname, lastname, role) VALUES "       
        for username, email, password, first, last, role in names_list:
            # hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

            # change it to string
            hashed_password = hashed_password.decode('utf-8')
            
            insert_user_sql += f"('{username}', '{email}', '{hashed_password}', '{first}', '{last}', '{role}'), "
            
        cursor.execute(insert_user_sql[:-2] + ";")

        insert_recipe_sql = "INSERT INTO recipe.Recipes (title, title_vector, type, description, instructions, description_vector, instructions_vector, calory, creatorID, lastUpdatorID) VALUES "
        for title, recipeType, description, instruction, calorie, user_id in recipe_list:
            title_vector = encode_text(title)
            description_vector = encode_text(description)
            instruction_vector = encode_text(instruction)
            
            insert_recipe_sql += f"('{title}', '{title_vector}', '{recipeType}', '{description}', '{instruction}', '{description_vector}', '{instruction_vector}', '{calorie}', '{user_id}', '{user_id}'), "
        cursor.execute(insert_recipe_sql[:-2] + ";")
        
        for query in db_setup:
            cursor.execute(query)

    except Exception as e:
        conn.rollback()
        print("*" * 70)
        print("An error occurred with PostgreSQL")
        print(e)

    finally:
        conn.commit()
        cursor.close()
        conn.close()