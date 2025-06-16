# image_server.py 최종 수정본

import os
from flask import Flask, Response, abort
import pymysql

app = Flask(__name__)

# DB 접속 정보 (사용자님 설정 그대로)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'rasa_core'
}

# 이미지 폴더 경로 (사용자님 설정 그대로)
BASE_IMAGE_DIR = "C:/pjw/image" # 슬래시(/) 사용을 권장하지만, 일단 그대로 둡니다.

@app.route('/image/<int:image_id>')
def get_image(image_id):
    conn = None
    cursor = None
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        # --- 바로 이 부분이 수정되었습니다! ---
        # 실제 테이블명 'images'와 실제 컬럼명 'name'을 사용하도록 변경
        cursor.execute("SELECT name FROM images WHERE id = %s", (image_id,))
        result = cursor.fetchone()

        if result and result[0]:
            image_file_name = result[0]
            image_path = os.path.join(BASE_IMAGE_DIR, image_file_name)

            if not os.path.isfile(image_path):
                abort(404, description="서버에 이미지 파일이 없습니다.")

            with open(image_path, 'rb') as f:
                image_data = f.read()

            # 확장자에 따라 MIME 타입 결정
            if image_path.lower().endswith('.png'):
                mime_type = 'image/png'
            elif image_path.lower().endswith('.webp'):
                mime_type = 'image/webp'
            else: # .jpg, .jpeg 등 나머지 경우는 jpeg로 처리
                mime_type = 'image/jpeg'

            return Response(image_data, mimetype=mime_type)
        else:
            abort(404, description=f"DB의 images 테이블에서 id={image_id}를 찾을 수 없습니다.")

    except Exception as e:
        print(f"이미지 서버 오류: {e}") # 디버그 모드에서 오류 확인용
        abort(500)
    finally:
        # DB 연결을 안전하게 닫기 위한 코드
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)