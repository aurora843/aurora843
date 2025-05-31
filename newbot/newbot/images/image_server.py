from flask import Flask, Response, abort
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',       # ← 수정 필요
    'database': 'rasa_core'      # ← 수정 필요
}

@app.route('/image/<int:image_id>')
def get_image(image_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM images WHERE id = %s", (image_id,))
        result = cursor.fetchone()

        if result and result[0]:
            image_data = result[0]
            return Response(image_data, mimetype='image/jpeg')
        else:
            abort(404, description="이미지를 찾을 수 없습니다.")

    except Exception as e:
        return f"오류 발생: {str(e)}", 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(port=8080)
