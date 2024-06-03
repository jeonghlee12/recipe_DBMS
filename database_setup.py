import psycopg2

def establish_connection():
    conn = psycopg2.connect(
        database="postgres",
        user='postgres',
        password='postgres',
        host='localhost',
        port= '5432'
    )
    return conn

def create_db():
    conn = establish_connection()
    cursor = conn.cursor()

    # Drop recipe schema if already exists.
    cursor.execute("DROP SCHEMA IF EXISTS recipe CASCADE")


    # Create schema and table
    sql ='''CREATE SCHEMA recipe;

    CREATE TABLE recipe.Users
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
        title VARCHAR(100),
        type VARCHAR(50),
        description TEXT,
        instructions TEXT,
        calory INTEGER,
        creatorID INTEGER NOT NULL,
        FOREIGN KEY (creatorID) REFERENCES recipe.users(userID)
    );

    '''
    cursor.execute(sql)
    print("Table created successfully........")

    conn.commit()
    conn.close()