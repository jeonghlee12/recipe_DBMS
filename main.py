from database_setup import create_db, initialize_db
# from user_operations import authenticate_user
# # from initialize_db import initialize
from functions import create_index, get_recommendations

def main():
    create_db()
    initialize_db()
    # initialize()
    createIndexScenario()
    recommendationScenario()
    # testScenario()

def createIndexScenario():
    # Performance Test of Index Scenario (Features : Index)
    # 1. Rating Table의 recipeID 열에 대해 Index 생성 전과 후의 성능 측정
    # 2. Record 수가 부족하여 강제로 Index Scan ON. 성능 차이 미미.
    print("*" * 50)
    print(f'******* Performance Test of Index Creation *******')
    print("*" * 50)
    create_index()
    
def recommendationScenario():
    # Recommendation Scenario (Features : Complex Query, Join, View, Partitioning)
    # 1. 비슷한 Rating(같은 Recipe Rating 3건 이상, 평균 평점 차이 2점 이내)을 주는 User들의 정보 관리(View Table) 
    # 2. 접속한 User의 SimilarUser들이(2명 이상) 높은 Rating(8점 이상)을 준 Recipe를 Type별(Partitioning) 1건씩 추천  
    current_user = 4
    recommendations = get_recommendations(user_id=current_user) # 접속한 user 4번
    print("*" * 50)
    print(f'********** Recommendation for User: {current_user} ************')
    print("*" * 50)
    for row in recommendations:
        print(f"Type: {row[0]}")
        print(f"Recipe ID: {row[1]}")
        print(f"Title: {row[2]}")
        print(f"Description: {row[3]}")
        print(f"Instructions: {row[4]}")
        print(f"Average Rating: {row[5]}")
        print(f"Rating Count: {row[6]}")
        print("-" * 50)


# def testScenario():
#     user1 = authenticate_user('david_lee', 'hashed_password_9')
#     result = user1.find_similar_recipes(description="a classic sandwich", min_calory=300, max_calory=550, num_results=3)
#     print("Finding similar recipes with similar description to 'classic' with a calories count between 300 and 550 - showing top 3 results")
#     for item in result:
#         print("---------------------------")
#         print("Title:", item[1])
#         print("Description:", item[2])
#         print("Instructions:", item[3])
#         print("Type:", item[4])
#         print("Calories:", item[5])


if __name__ == "__main__":
    main()