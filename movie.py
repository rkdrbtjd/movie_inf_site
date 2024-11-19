import pandas as pd
import mysql.connector
import bcrypt

#CSV파일 로드
movie_data = pd.read_csv(r"C:\Users\강규성\Documents\Python Scripts\movie_data.csv", encoding='cp949')

# 파이썬과 MySQL 연동
conn = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)
cursor = conn.cursor(dictionary = True)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def register_user():
    print("\n========== 회원가입 ==========")
    username = input("아이디: ")
    name = input("이름: ")
    gender = input("성별 (M/F/Other): ")
    birthdate = input("생년월일 (YYYY-MM-DD): ")
    email = input("이메일: ")
    password = input("비밀번호: ")
    password_confirm = input("비밀번호 확인: ")

    # 비밀번호 확인 일치 여부 확인
    if password != password_confirm:
        print("비밀번호가 일치하지 않습니다.")
        return
    
    # 비밀번호 해싱
    hashed_password = hash_password(password)
    
    # 사용자 & 관리자 선택
    role = input("가입 유형을 입력하세요 ('admin' 또는 'user') [기본값: 'user']: ") or 'user'
    if role not in ['admin', 'user']:
        print("잘못된 역할입니다. 기본적으로 'user'로 등록됩니다.")
        role = 'user'

    # 데이터베이스에 사용자 추가 (user_id는 자동 증가로 설정되어 있기 때문에 제외)
    query = """
    INSERT INTO User (username, name, gender, birthdate, password, email, role)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (username, name, gender, birthdate, hashed_password, email, role)
    
    try:
        cursor.execute(query, values)
        conn.commit()
        print(f"사용자 '{username}'가 성공적으로 등록되었습니다.")
    except mysql.connector.IntegrityError:
        print("이미 존재하는 사용자명 또는 이메일입니다.")

# 로그인 함수
def login_user():
    print("\n========== 로그인 ==========")
    username = input("사용자명: ")
    password = input("비밀번호: ")

    # 사용자 정보 조회
    query = "SELECT * FROM User WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    if user:
        # 비밀번호 검증
        if check_password(user['password'], password):
            print(f"{username}님, 로그인에 성공하였습니다.")
            return user
        else:
            print("비밀번호가 일치하지 않습니다.")
    else:
        print("존재하지 않는 사용자명입니다.")
    return None


#로그인 함수
def login_user():
    print("\n========== 로그인 ==========")
    username = input("사용자명: ")
    password = input("비밀번호: ")

    # 사용자 정보 조회
    query = "SELECT * FROM User WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    if user:
        # 비밀번호 검증
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            print(f"{username}님, 로그인에 성공하였습니다.")
            return user  # 로그인 성공 시 사용자 정보 반환
        else:
            print("비밀번호가 일치하지 않습니다.")
    else:
        print("존재하지 않는 사용자명입니다.")
    return None  # 로그인 실패 시 None 반환

#==================================관리자 인터페이스===============================

# 영화 테이블 전체 조회 코드
def fetch_all_movies():
    query = "SELECT * FROM Movie ORDER BY release_date ASC"
    cursor.execute(query)
    results = cursor.fetchall()
    if results:
        print("\n========== 전체 영화 목록 ==========")
        for movie in results:
            print(f"ID: {movie['movie_id']}, Title: {movie['title']}, Director: {movie['director']}, "
                  f"Actor: {movie['actor']}, Genre: {movie['genre']}, Release Date: {movie['release_date']}, "
                  f"Distributor: {movie['distributor']}, Running Time: {movie['running_time']}, "
                  f"Rating: {movie['rating']}, Running State: {movie['running_state']}")
    else:
        print("영화 목록이 없습니다.")
        
        
# 영화 정보 추가 코드
def add_movie():
    # 사용자로부터 영화 정보 입력 받기
    movie_id = input("monvie_id : ")
    title = input("title: ")
    distributor = input("distributor: ")
    director = input("director: ")
    actor = input("actor: ")
    genre = input("genre: ")
    release_date = input("release_date (YYYY-MM-DD 형식): ")
    running_time = input("running_time (예: 120 min): ")
    rating = float(input("rating (0.0 ~ 10.0 사이의 값): "))
    running_state = input("running_stata (Yes/No): ")

    # 영화 정보를 데이터베이스에 추가하는 쿼리
    query = """
    INSERT INTO Movie (movie_id, title, distributor, director, actor, genre, release_date, running_time, rating, running_state)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (movie_id, title, distributor, director, actor, genre, release_date, running_time, rating, running_state)
    
    # 쿼리 실행
    cursor.execute(query, values)
    conn.commit()  # 변경 사항을 커밋하여 데이터베이스에 반영

    print(f"영화 '{title}' 정보가 성공적으로 추가되었습니다.")


# 영화 정보 수정 코드
def modify_movie():
    movie_id = input("수정할 영화의 번호을 입력하세요: ")
    
    # 현재 영화 정보를 조회
    query = "SELECT * FROM Movie WHERE movie_id = %s"
    cursor.execute(query, (movie_id,))
    movie = cursor.fetchone()
    
    if movie:
        print("\n수정할 영화 정보를 입력하세요. 수정하지 않으려면 Enter를 눌러주세요.")
        
        # 각 항목에 대해 수정 여부 확인 (현재 값 제공)
        title = input(f"Title (현재: {movie['title']}): ") or movie['title']
        distributor = input(f"Distributor (현재: {movie['distributor']}): ") or movie['distributor']
        director = input(f"Director (현재: {movie['director']}): ") or movie['director']
        actor = input(f"Actor (현재: {movie['actor']}): ") or movie['actor']
        genre = input(f"Genre (현재: {movie['genre']}): ") or movie['genre']
        release_date = input(f"Release Date (현재: {movie['release_date']}): ") or movie['release_date']
        running_time = input(f"Running Time (현재: {movie['running_time']}): ") or movie['running_time']
        rating = input(f"Rating (현재: {movie['rating']}): ") or movie['rating']
        running_state = input(f"Running State (현재: {movie['running_state']}): ") or movie['running_state']
        
        # 수정된 값만으로 업데이트 쿼리 작성
        query = """
        UPDATE Movie 
        SET title = %s, distributor = %s, director = %s, actor = %s, genre = %s, 
            release_date = %s, running_time = %s, rating = %s, running_state = %s 
        WHERE movie_id = %s
        """
        
        values = (title, distributor, director, actor, genre, release_date, running_time, rating, running_state, movie_id)
        
        cursor.execute(query, values)
        conn.commit()  # 변경 사항을 커밋하여 데이터베이스에 반영

        print(f"영화 '{title}' 정보가 성공적으로 수정되었습니다.")
    else:
        print("해당 ID의 영화가 존재하지 않습니다.")

def search_movie():
    title = input("검색할 영화 제목을 입력하세요: ")
    query = "SELECT * FROM Movie WHERE title LIKE %s"
    cursor.execute(query, ('%' + title + '%',))
    results = cursor.fetchall()
    
    if results:
        print("\n========== 영화 검색 결과 ==========")
        for movie in results:
            print(f"ID: {movie['movie_id']}, Title: {movie['title']}, Director: {movie['director']}, "
                  f"Genre: {movie['genre']}, Release Date: {movie['release_date']}")
    else:
        print("검색 결과가 없습니다.")

#==================================사용자 인터페이스===============================

#사용자 영화 검색 함수
def search_movie():
    print("\n========== 영화 검색 ==========")
    title = input("검색할 영화 제목을 입력하세요: ")

    # SQL 쿼리: 제목에 사용자가 입력한 텍스트가 포함된 영화를 검색
    query = "SELECT * FROM Movie WHERE title LIKE %s"
    cursor.execute(query, ('%' + title + '%',))
    results = cursor.fetchall()

    # 검색 결과 출력
    if results:
        print("\n========== 검색 결과 ==========")
        for movie in results:
            print(f"ID: {movie['movie_id']}, Title: {movie['title']}, Director: {movie['director']}, "
                  f"Actor: {movie['actor']}, Genre: {movie['genre']}, Release Date: {movie['release_date']}, "
                  f"Distributor: {movie['distributor']}, Running Time: {movie['running_time']}, "
                  f"Rating: {movie['rating']}, Running State: {movie['running_state']}")
    else:
        print("검색 결과가 없습니다.")


# 사용자 리뷰 작성 함수
def write_review(current_user):
    print("\n========== 리뷰 작성 ==========")
    movie_title = input("리뷰를 작성할 영화의 제목을 입력하세요: ")
    review_text = input("리뷰 내용을 입력하세요: ")

    # 영화 ID 가져오기
    query = "SELECT movie_id FROM Movie WHERE title = %s"
    cursor.execute(query, (movie_title,))
    movie = cursor.fetchone()

    if not movie:
        print("존재하지 않는 영화 제목입니다. 리뷰 작성이 불가능합니다.")
        return

    movie_id = movie['movie_id']

    # 현재 로그인된 사용자 ID가 필요
    user_id = current_user['user_id']  # 로그인된 사용자 정보에서 가져옴

    # 리뷰 추가 쿼리
    query = """
    INSERT INTO Review (user_id, movie_id, review_text, review_date)
    VALUES (%s, %s, %s, CURDATE())
    """
    values = (user_id, movie_id, review_text)

    try:
        cursor.execute(query, values)
        conn.commit()
        print("리뷰가 성공적으로 작성되었습니다.")
    except Exception as e:
        print("리뷰 작성 오류:", e)


# 사용자 평점 작성 함수
def write_rating(current_user):
    print("\n========== 평점 작성 ==========")
    movie_title = input("평점을 작성할 영화의 제목을 입력하세요: ")
    rating_value = float(input("평점을 입력하세요 (0.0 ~ 10.0): "))

    # 평점 유효성 확인
    if not (0.0 <= rating_value <= 10.0):
        print("평점은 0과 10사이의 값이어야 합니다.")
        return

    # 영화 ID 가져오기
    query = "SELECT movie_id FROM Movie WHERE title = %s"
    cursor.execute(query, (movie_title,))
    movie = cursor.fetchone()

    if not movie:
        print("존재하지 않는 영화 제목입니다. 평점 작성이 불가능합니다.")
        return

    movie_id = movie['movie_id']

    # 현재 로그인된 사용자 ID가 필요
    user_id = current_user['user_id']  # 로그인된 사용자 정보에서 가져옴

    # 기존 평점 존재 여부 확인
    query = "SELECT * FROM Rating WHERE user_id = %s AND movie_id = %s"
    cursor.execute(query, (user_id, movie_id))
    existing_rating = cursor.fetchone()

    if existing_rating:
        print("이미 이 영화에 대해 평점을 작성하셨습니다. 업데이트를 진행합니다.")
        query = "UPDATE Rating SET rating_value = %s WHERE user_id = %s AND movie_id = %s"
        values = (rating_value, user_id, movie_id)
    else:
        # 새로운 평점 추가
        query = """
        INSERT INTO Rating (user_id, movie_id, rating_value)
        VALUES (%s, %s, %s)
        """
        values = (user_id, movie_id, rating_value)

    try:
        cursor.execute(query, values)
        conn.commit()
        print("평점이 성공적으로 작성되었습니다.")
    except Exception as e:
        print("평점 작성 오류:", e)



#인터페이스
def menu():
    current_user = None  # 현재 로그인한 사용자 정보를 저장하는 변수
    
    while True:
        print("\n영화 정보 시스템")
        if current_user is None:
            print("1. 회원가입")
            print("2. 로그인")
            print("3. 종료")
            choice = input("원하는 작업의 번호를 입력하세요: ")
            
            if choice == '1':
                register_user()
            elif choice == '2':
                current_user = login_user()  # 로그인 후 사용자 정보 저장
            elif choice == '3':
                print("프로그램을 종료합니다.")
                break
            else:
                print("잘못된 입력입니다. 다시 시도해주세요.")
        else:
            role = current_user['role']
            print(f"\n환영합니다, {current_user['username']}님 ({role})")
            if role == 'admin':
                # 관리자 메뉴
                print("1. 전체 영화 목록 조회")
                print("2. 영화 추가")
                print("3. 영화 정보 수정")
                print("4. 로그아웃")
                print("5. 종료")
                
                choice = input("원하는 작업의 번호를 입력하세요: ")
                
                if choice == '1':
                    fetch_all_movies()
                elif choice == '2':
                    add_movie()
                elif choice == '3':
                    modify_movie()
                elif choice == '4':
                    current_user = None
                    print("로그아웃되었습니다.")
                elif choice == '5':
                    print("프로그램을 종료합니다.")
                    break
                else:
                    print("잘못된 입력입니다. 다시 시도해주세요.")
            
            elif role == 'user':
                # 사용자 메뉴
                print("1. 영화 검색")
                print("2. 리뷰 작성")
                print("3. 평점 작성")
                print("4. 로그아웃")
                print("5. 종료")
                
                choice = input("원하는 작업의 번호를 입력하세요: ")
                
                if choice == '1':
                    search_movie()
                elif choice == '2':
                    write_review(current_user)
                elif choice == '3':
                    write_rating(current_user)
                elif choice == '4':
                    current_user = None
                    print("로그아웃되었습니다.")
                elif choice == '5':
                    print("프로그램을 종료합니다.")
                    break
                else:
                    print("잘못된 입력입니다. 다시 시도해주세요.")


menu()
