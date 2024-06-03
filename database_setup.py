import psycopg2
from transformers import AutoTokenizer, AutoModel
import torch

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
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        firstname VARCHAR(50),
        lastname VARCHAR(50),
        role VARCHAR(20) DEFAULT 'user',
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
        avgRating DECIMAL CHECK (avgRating >= 0 AND avgRating <= 10),
        beingEdited  BOOL DEFAULT FALSE,
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
        FOREIGN KEY (userID) REFERENCES recipe.Users(userID),
        FOREIGN KEY (recipeID) REFERENCES recipe.Recipes(recipeID)
    );
    '''
    cursor.execute(create_table_sql)

    # Create triggers for updating timestamp
    triggers_sql = """CREATE OR REPLACE FUNCTION upd_timestamp() RETURNS TRIGGER
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
    cursor.execute(triggers_sql)

    conn.commit()
    conn.close()

def initialize_db():
    # Fill tables
    with open('setup_queries.md', 'r') as file:
        queries = file.read()

    queries = queries.split(';')
    queries = [q.strip() for q in queries if q.strip()]

    conn = establish_connection()
    if conn is None:
        print("No connection to PostgreSQL!")
        return
    
    try:
        cursor = conn.cursor()
        for query in queries:
            cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")