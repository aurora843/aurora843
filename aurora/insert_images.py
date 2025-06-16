import pymysql

# DB 연결
conn = pymysql.connect(
    host='localhost',
    user='rasauser',
    password='rasa1234',
    db='rasa',
    charset='utf8'
)

cursor = conn.cursor()

# 삽입할 이미지 정보
image_data = [
    ('cleaning_rules', 'images/cleaning_rules.png'),
    ('laundry_rules', 'images/laundry_rules.png')
]

# 데이터 삽입
for rule_type, image_path in image_data:
    sql = "INSERT INTO image_rules (rule_type, image_path) VALUES (%s, %s)"
    cursor.execute(sql, (rule_type, image_path))

conn.commit()
print("이미지 경로 저장 완료!")

cursor.close()
conn.close()
