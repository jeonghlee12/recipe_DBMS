import psycopg2

db_config = {
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

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