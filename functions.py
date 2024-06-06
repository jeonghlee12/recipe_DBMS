import psycopg2
import time

db_config = {
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

def execute_explain_analyze(query, db_config):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute(f"SET enable_seqscan TO OFF; EXPLAIN ANALYZE {query}")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def execute_query(query, db_config):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

def create_index():
    # 쿼리
    query = "SELECT AVG(rating) FROM recipe.Rating WHERE recipeID = 1;"

    # 쿼리 실행 전 성능 측정
    result_before = execute_explain_analyze(query, db_config)
    print("Execution plan and time before index creation:")
    print("-" * 50)
    for row in result_before:
        print(row[0])
    print("-" * 50)

    # 인덱스 생성
    index_query = "CREATE INDEX idx_recipeID ON recipe.Rating(recipeID);"
    execute_query(index_query, db_config)
    print("Index created!")
    print("-" * 50)
    
    # 쿼리 실행 후 성능 측정
    result_after = execute_explain_analyze(query, db_config)
    print("Execution plan and time after index creation:")
    print("-" * 50)
    for row in result_after:
        print(row[0])
    print("-" * 50)

    # 인덱스 제거 (옵션)
    drop_index_query = "DROP INDEX recipe.idx_recipeID; SET enable_seqscan TO ON;"
    execute_query(drop_index_query, db_config)

def get_recommendations(user_id):
    # 데이터베이스에 연결
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # SimilarUsers 뷰를 생성하는 쿼리
    create_view_query = """
    CREATE OR REPLACE VIEW recipe.SimilarUsers AS
    WITH UserRatings AS (
        SELECT
            userID,
            recipeID,
            rating
        FROM
            recipe.Rating
    )
    SELECT
        ur1.userID AS userID,
        ur2.userID AS similarUserID,
        COUNT(*) AS commonRatings,
        AVG(ABS(ur1.rating - ur2.rating)) AS avgRatingDifference
    FROM
        UserRatings ur1
    JOIN
        UserRatings ur2
    ON
        ur1.recipeID = ur2.recipeID
        AND ur1.userID != ur2.userID
    GROUP BY
        ur1.userID, ur2.userID
    HAVING
        COUNT(*) >= 3
        AND AVG(ABS(ur1.rating - ur2.rating)) < 2;
    """
    
    # 뷰 생성
    cur.execute(create_view_query)
    conn.commit()

    # 추천 쿼리
    recommendation_query = """
    WITH UserRatings AS (
        SELECT
            userID,
            recipeID,
            rating
        FROM
            recipe.Rating
    ),
    UserSimilarUsers AS (
        SELECT
            su.similarUserID
        FROM
            recipe.SimilarUsers su
        WHERE
            su.userID = """ + str(user_id) + """
    ),
    SimilarUserRatings AS (
        SELECT
            ru.recipeID,
            ru.rating,
            r.type
        FROM
            UserSimilarUsers su
        JOIN
            UserRatings ru ON su.similarUserID = ru.userID
        JOIN
            recipe.Recipes r ON ru.recipeID = r.recipeID
    ),
    TopRatedRecipes AS (
        SELECT
            sur.recipeID,
            sur.type,
            AVG(sur.rating) AS avgRating,
            COUNT(*) AS ratingCount
        FROM
            SimilarUserRatings sur
        WHERE
            sur.rating >= 8
        GROUP BY
            sur.recipeID, sur.type
        HAVING
            COUNT(*) >= 2
    ),
    RankedRecipes AS (
        SELECT
            tr.type,
            tr.recipeID,
            r.title,
            r.description,
            r.instructions,
            tr.avgRating,
            tr.ratingCount,
            ROW_NUMBER() OVER (PARTITION BY tr.type ORDER BY tr.avgRating DESC) AS rank
        FROM
            TopRatedRecipes tr
        JOIN
            recipe.Recipes r ON tr.recipeID = r.recipeID
    )
    SELECT
        type,
        recipeID,
        title,
        description,
        instructions,
        avgRating,
        ratingCount
    FROM
        RankedRecipes
    WHERE
        rank = 1;
    """
    
    # 추천 쿼리 실행
    cur.execute(recommendation_query)
    recommendations = cur.fetchall()

    # 연결 닫기
    cur.close()
    conn.close()

    # 추천 결과 반환
    return recommendations