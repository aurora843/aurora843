import mysql.connector
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
            password='123456',
            database='rasa_core'
        )
        cursor = conn.cursor()

        try:
            # 연락처 카테고리 목록 요청
            if "연락처 목록" in user_message or "번호 목록" in user_message or "전화번호" in user_message:
                query = "SELECT DISTINCT `구분` FROM number"
                cursor.execute(query)
                rows = cursor.fetchall()
                if rows:
                    categories = [row[0] for row in rows]
                    result = "\n- " + "\n- ".join(categories)
                    dispatcher.utter_message(text=f"📞 현재 등록된 연락처 카테고리는 다음과 같습니다:\n{result}")
                else:
                    dispatcher.utter_message(text="연락처 카테고리가 등록되어 있지 않습니다.")
                return []

            # 규칙 카테고리 목록 요청
            if "규칙 목록" in user_message or "규칙 리스트" in user_message or "카테고리" in user_message:
                query = "SELECT DISTINCT `구분 (Category)` FROM chatbot"
                cursor.execute(query)
                rows = cursor.fetchall()
                if rows:
                    categories = [row[0] for row in rows]
                    result = "\n- " + "\n- ".join(categories)
                    dispatcher.utter_message(text=f"📚 현재 가능한 규칙 카테고리는 다음과 같습니다:\n{result}")
                else:
                    dispatcher.utter_message(text="등록된 카테고리가 없습니다.")
                return []

            # 규칙 카테고리 판별
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

            # 연락처 구분 유사 매칭 및 세부항목 출력
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
                    lines = [f"- {row[0]} → {row[1]}" for row in rows]
                    result = "\n".join(lines)
                    dispatcher.utter_message(text=f"📞 [{matched_category}] 연락처 세부항목 목록입니다:\n{result}")
                else:
                    dispatcher.utter_message(text="해당 구분에 연락처 세부항목이 없습니다.")
                return []

            # 규칙 카테고리 세부 내용 + 이미지 동시 출력
            if category:
                # 텍스트 출력
                query = "SELECT `세부 항목 (Sub-category/Item)`, `상세 내용 (Details)` FROM chatbot WHERE `구분 (Category)` = %s"
                cursor.execute(query, (category,))
                rows = cursor.fetchall()

                if rows:
                    lines = [f"{i+1}. {row[0]} → {row[1]}" for i, row in enumerate(rows)]
                    result = "\n\n".join(lines)
                    dispatcher.utter_message(text=f"📚 [{category} 안내]\n\n{result}")
                else:
                    dispatcher.utter_message(text="해당 규칙을 찾을 수 없습니다.")
                    return []

                # 이미지 출력 (텍스트와 함께)
                category_image_ids = {
                    "일반 규칙": 1,
                    "기숙사 시설 이용": 2,
                    "주의사항 (화재)": 3,
                    "주의사항 (화상)": 4,
                    "기타 주의사항": 5,
                    "금지 행위": 6,
                    "상벌 제도": 7,
                    "세탁 카페": 8,
                    "버스 시간표": 9,
                    "연락처 정보": 10
                }

                if category in category_image_ids:
                    image_id = category_image_ids[category]
                    image_url = f"http://127.0.0.1:8080/image/{image_id}"
                    dispatcher.utter_message(image=image_url)
                else:
                    query_img = "SELECT image_id FROM rule_images WHERE category = %s"
                    cursor.execute(query_img, (category,))
                    image_rows = cursor.fetchall()
                    if image_rows:
                        for image_row in image_rows:
                            image_url = f"http://127.0.0.1:8080/image/{image_row[0]}"
                            dispatcher.utter_message(image=image_url)
                    else:
                        dispatcher.utter_message(text="해당 카테고리에 대한 이미지를 찾을 수 없습니다.")
                return []

            # 연락처 세부항목 직접 매칭
            query = "SELECT `세부항목`, `상세내용` FROM number"
            cursor.execute(query)
            all_sub_items = cursor.fetchall()
            matched_sub_item = None
            for sub_item, detail in all_sub_items:
                if sub_item in user_message or user_message in sub_item:
                    matched_sub_item = (sub_item, detail)
                    break

            if matched_sub_item:
                sub_name, sub_detail = matched_sub_item
                dispatcher.utter_message(text=f"{sub_detail}")
                return []

            # 그 외 아무 조건에도 해당하지 않을 경우
            dispatcher.utter_message(text="죄송해요. 해당 내용을 이해하지 못했어요. 다시 질문해 주세요.")
            return []

        finally:
            cursor.close()
            conn.close()
