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
    with open('setup_queries.md', 'r') as file:
        queries = file.read()

    queries = queries.split(';')
    queries = [q.strip() for q in queries if q.strip()]

    try:
        cursor = conn.cursor()
        for query in queries:
            cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database setup completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")