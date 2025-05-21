import mysql.connector
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List

class ActionChatBot(Action):
    def name(self) -> Text:
        return "action_chatbot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text')

        # 카테고리 매칭
        if "일반 규칙" in user_message:
            category = "일반 규칙"
        elif "기숙사 시설 이용" in user_message:
            category = "기숙사 시설 이용"
        elif "목록" in user_message:
            category = "구분"    
        elif "주의사항 (화재)" in user_message or "화재" in user_message:
            category = "주의사항 (화재)"
        elif "주의사항 (화상)" in user_message or "화상" in user_message:
            category = "주의사항 (화상)"
        elif "기타 주의사항" in user_message:
            category = "기타 주의사항"
        elif "금지 행위" in user_message:
            category = "금지 행위"
        elif "상벌 제도" in user_message:
            category = "상벌 제도"
        elif "세탁 카페" in user_message:
            category = "세탁 카페"
        elif "버스 시간표" in user_message or "버스" in user_message:
            category = "버스 시간표"
        elif "연락처 정보" in user_message or "연락처" in user_message or "전화번호" in user_message:
            category = "연락처 정보"
        else:
            dispatcher.utter_message(text="죄송해요. 해당 규칙 카테고리를 찾을 수 없습니다.")
            return []

        # MySQL 연결
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='1234',
            database='Local instance MYSQL80'
        )
        cursor = conn.cursor()

        # 해당 카테고리 항목 가져오기
        query = "SELECT `세부 항목 (Sub-category/Item)`, `상세 내용 (Details)` FROM chatbot WHERE `구분 (Category)` = %s"
        cursor.execute(query, (category,))
        rows = cursor.fetchall()

        # 숫자 정렬
        if rows:
            messages = [f"{idx+1}. {row[0]} → {row[1]}" for idx, row in enumerate(rows)]
            result = "\n\n".join(messages)
            dispatcher.utter_message(text=f"📚 [{category} 안내]\n\n{result}")
        else:
            dispatcher.utter_message(text="해당 규칙을 찾을 수 없습니다.")

        cursor.close()
        conn.close()
        return []
