import mysql.connector
import pymysql
pymysql.install_as_MySQLdb()
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
import difflib

class ActionChatBot(Action):
    def name(self) -> Text:
        return "action_chatbot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text')

        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='1234',
            database='rasa_core'
        )
        cursor = conn.cursor()

        try:
            # 1. 연락처 카테고리 목록 요청
            if "연락처 목록" in user_message or "연락처 카테고리" in user_message or "연락처 종류" in user_message:
                query = "SELECT DISTINCT `구분` FROM number"
                cursor.execute(query)
                rows = cursor.fetchall()
                if rows:
                    result = "\n- " + "\n- ".join([row[0] for row in rows])
                    dispatcher.utter_message(text=f"📞 현재 등록된 연락처 카테고리는 다음과 같습니다:\n{result}")
                else:
                    dispatcher.utter_message(text="연락처 카테고리가 등록되어 있지 않습니다.")
                return []

            # 2. 규칙 카테고리 목록 요청
            if "규칙" in user_message or "규칙 리스트" in user_message or "카테고리" in user_message:
                query = "SELECT DISTINCT `구분 (Category)` FROM chatbot"
                cursor.execute(query)
                rows = cursor.fetchall()
                if rows:
                    result = "\n- " + "\n- ".join([row[0] for row in rows])
                    dispatcher.utter_message(text=f"📚 현재 가능한 규칙 카테고리는 다음과 같습니다:\n{result}")
                else:
                    dispatcher.utter_message(text="등록된 카테고리가 없습니다.")
                return []

            # 3. 규칙 카테고리 판별
            category = None
            if "일반 규칙" in user_message:
                category = "일반 규칙"
            elif "기숙사 시설 이용" in user_message or "기숙사" in user_message:
                category = "기숙사 시설 이용"
            elif "주의사항 (화재)" in user_message or "화재" in user_message:
                category = "주의사항 (화재)"
            elif "주의사항 (화상)" in user_message or "화상" in user_message:
                category = "주의사항 (화상)"
            elif "기타 주의사항" in user_message or "기타" in user_message:
                category = "기타 주의사항"
            elif "금지 행위" in user_message or "금지" in user_message:
                category = "금지 행위"
            elif "상벌 제도" in user_message or "상벌" in user_message:
                category = "상벌 제도"
            elif "세탁 카페" in user_message or "세탁" in user_message:
                category = "세탁 카페"
            elif "버스 시간표" in user_message or "버스" in user_message:
                category = "버스 시간표"

            # 4. 연락처 구분 유사 매칭
            query = "SELECT DISTINCT `구분` FROM number"
            cursor.execute(query)
            all_categories = [row[0] for row in cursor.fetchall()]
            matched_category = None
            matches = difflib.get_close_matches(user_message, all_categories, n=1, cutoff=0.5)
            if matches:
                matched_category = matches[0]
            else:
                for cat in all_categories:
                    if cat in user_message or user_message in cat:
                        matched_category = cat
                        break

            if matched_category:
                query = "SELECT `세부항목`, `상세내용` FROM number WHERE `구분` = %s"
                cursor.execute(query, (matched_category,))
                rows = cursor.fetchall()
                if rows:
                    result = "\n".join([f"- {row[0]} → {row[1]}" for row in rows])
                    dispatcher.utter_message(text=f"📞 [{matched_category}] 연락처 세부항목 목록입니다:\n{result}")
                else:
                    dispatcher.utter_message(text="해당 구분에 연락처 세부항목이 없습니다.")
                return []

            # 5. 규칙 세부 내용 출력
            if category:
                query = "SELECT `세부 항목 (Sub-category/Item)`, `상세 내용 (Details)` FROM chatbot WHERE `구분 (Category)` = %s"
                cursor.execute(query, (category,))
                rows = cursor.fetchall()
                if rows:
                    result = "\n".join([f"- {sub} → {detail}" for sub, detail in rows])
                    dispatcher.utter_message(text=f"📚 [{category} 안내]\n{result}")
                else:
                    dispatcher.utter_message(text="해당 규칙을 찾을 수 없습니다.")
                return []

            # 6. 세부항목 직접 매칭
            query = "SELECT `세부항목`, `상세내용` FROM number"
            cursor.execute(query)
            all_sub_items = cursor.fetchall()
            for sub_item, detail in all_sub_items:
                if sub_item in user_message or user_message in sub_item:
                    dispatcher.utter_message(text=f"📞 [{sub_item}] 상세 정보:\n{detail}")
                    return []

            # 7. 아무것도 해당하지 않음
            dispatcher.utter_message(text="죄송해요. 해당 내용을 이해하지 못했어요. 다시 질문해 주세요.")
            return []

        finally:
            cursor.close()
            conn.close()

class ActionShowCleaningImage(Action):
    def name(self):
        return "action_show_cleaning_image"

    def run(self, dispatcher, tracker, domain):
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='1234',
            db='rasa_core',
            charset='utf8'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT image_path FROM image_rules WHERE rule_type = 'cleaning_rules'")
        result = cursor.fetchone()
        if result:
            dispatcher.utter_message(text="다음은 청소 관련 이미지입니다:")
            dispatcher.utter_message(image=result[0])
        else:
            dispatcher.utter_message(text="이미지를 찾을 수 없습니다.")
        cursor.close()
        conn.close()
        return []

class ActionShowLaundryImage(Action):
    def name(self):
        return "action_show_laundry_image"

    def run(self, dispatcher, tracker, domain):
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='1234',
            db='rasa_core',
            charset='utf8'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT image_path FROM image_rules WHERE rule_type = 'laundry_rules'")
        result = cursor.fetchone()
        if result:
            dispatcher.utter_message(text="다음은 세탁 관련 이미지입니다:")
            dispatcher.utter_message(image=result[0])
        else:
            dispatcher.utter_message(text="이미지를 찾을 수 없습니다.")
        cursor.close()
        conn.close()
        return []
