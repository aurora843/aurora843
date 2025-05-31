import pymysql

# DB 연결
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',   # ← 본인의 MySQL 비밀번호로 수정
    db='rasa_core',
    charset='utf8'
)
cursor = conn.cursor()

# 이미지 파일 읽기
with open('cleaning_rules.png', 'rb') as file:  # ← 복사한 이미지 이름으로 수정
    binary_data = file.read()

# DB에 저장
sql = "INSERT INTO images (name, data) VALUES (%s, %s)"
cursor.execute(sql, ('cleaning_rules.png', binary_data))  # ← 파일명 동일하게

conn.commit()
cursor.close()
conn.close()

print("이미지 업로드 성공")