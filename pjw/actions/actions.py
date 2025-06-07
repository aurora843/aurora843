import mysql.connector
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
import difflib
from googletrans import Translator

class ActionChatBot(Action):

    def name(self) -> Text:
        return "action_chatbot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        original_message = tracker.latest_message.get('text')
        translator = Translator()

        # 언어 감지 및 번역 
        detected_lang = translator.detect(original_message).lang
        translated_msg = original_message
        if detected_lang != 'ko':
            translated_msg = translator.translate(original_message, src=detected_lang, dest='ko').text

        # DB 연결
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='123456', 
            database='rasa_core'
        )
        cursor = conn.cursor()

        try:
            category = None
            # 규칙 관련 키워드가 포함되어 있는지 확인하고 카테고리 설정
            if "규칙" in translated_msg:
                if "일반 규칙" in translated_msg:
                    category = "일반 규칙"
                elif "기숙사 시설 이용" in translated_msg or "기숙사" in translated_msg:
                    category = "기숙사 시설 이용"
                elif "주의사항 (화재)" in translated_msg or "화재" in translated_msg:
                    category = "주의사항 (화재)"
                elif "주의사항 (화상)" in translated_msg or "화상" in translated_msg:
                    category = "주의사항 (화상)"
                elif "기타 주의사항" in translated_msg or "기타" in translated_msg:
                    category = "기타 주의사항"
                elif "금지 행위" in translated_msg or "금지" in translated_msg:
                    category = "금지 행위"
                elif "상벌 제도" in translated_msg or "상벌" in translated_msg:
                    category = "상벌 제도"
                elif "세탁 카페" in translated_msg or "세탁" in translated_msg:
                    category = "세탁 카페"
                elif "버스 시간표" in translated_msg or "버스" in translated_msg:
                    category = "버스 시간표"

            image_url = None
            if category:
                # 이미지 먼저 가져오기
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
                    image_id = category_image_ids.get(category)
                    image_url = f"http://127.0.0.1:8080/image/{image_id}"
                else:
                    query_img = "SELECT image_id FROM rule_images WHERE category = %s"
                    cursor.execute(query_img, (category,))
                    image_rows = cursor.fetchall()
                    if image_rows:
                        image_id = image_rows[0][0]
                        image_url = f"http://127.0.0.1:8080/image/{image_id}"

                # 규칙 내용 가져오기
                query_text = "SELECT `세부 항목 (Sub-category/Item)`, `상세 내용 (Details)` FROM chatbot WHERE `구분 (Category)` = %s"
                cursor.execute(query_text, (category,))
                rows_text = cursor.fetchall()

                final_message = ""
                if image_url:
                    dispatcher.utter_message(image=image_url)
                else:
                    final_message += "해당 규칙에 대한 이미지를 찾을 수 없습니다.\n\n" 

                if rows_text:
                    # '연락처' 부분처럼 '상세 내용 (Details)'만 나열되도록 수정
                    lines = [f"- {row_text[1]}" for row_text in rows_text]
                    result_text = "\n".join(lines)
                    final_message += f"📚 [{category} 안내] 목록입니다:\n{result_text}"
                else:
                    final_message += f"📚 [{category} 안내]\n해당 규칙에 대한 자세한 내용을 찾을 수 없습니다."

                final_translated_message = translator.translate(final_message, src='ko', dest=detected_lang).text if detected_lang != 'ko' else final_message
                dispatcher.utter_message(text=final_translated_message)
                return []

            # ------------------- 연락처 카테고리 목록 요청 -------------------
            if "연락처 목록" in translated_msg or "연락처 카테고리" in translated_msg or "연락처 종류" in translated_msg:
                query = "SELECT DISTINCT `구분` FROM number"
                cursor.execute(query)
                rows = cursor.fetchall()

                if rows:
                    categories = [row[0] for row in rows]
                    result = "\n- " + "\n- ".join(categories)
                    message = f"📞 현재 등록된 연락처 카테고리는 다음과 같습니다:\n{result}"
                else:
                    message = "연락처 카테고리가 등록되어 있지 않습니다."

                final_msg = translator.translate(message, src='ko', dest=detected_lang).text if detected_lang != 'ko' else message
                dispatcher.utter_message(text=final_msg)
                return []

            # ------------------- 규칙 카테고리 목록 요청 -------------------
            if "규칙" in translated_msg and ("목록" in translated_msg or "리스트" in translated_msg or "카테고리" in translated_msg):
                query = "SELECT DISTINCT `구분 (Category)` FROM chatbot"
                cursor.execute(query)
                rows = cursor.fetchall()

                if rows:
                    categories = [row[0] for row in rows]
                    result = "\n- " + "\n- ".join(categories)
                    message = f"📚 현재 가능한 규칙 카테고리는 다음과 같습니다:\n{result}"
                else:
                    message = "등록된 카테고리가 없습니다."

                final_msg = translator.translate(message, src='ko', dest=detected_lang).text if detected_lang != 'ko' else message
                dispatcher.utter_message(text=final_msg)
                return []

            # ------------------- 연락처 구분 유사 매칭 -------------------
            query = "SELECT DISTINCT `구분` FROM number"
            cursor.execute(query)
            all_contact_categories = [row[0] for row in cursor.fetchall()]

            matched_contact_category = None
            matches = difflib.get_close_matches(translated_msg, all_contact_categories, n=1, cutoff=0.5)
            if matches:
                matched_contact_category = matches[0]
            else:
                for cat in all_contact_categories:
                    if cat in translated_msg or translated_msg in cat:
                        matched_contact_category = cat
                        break

            if matched_contact_category:
                query = "SELECT `세부항목`, `상세내용` FROM number WHERE `구분` = %s"
                cursor.execute(query, (matched_contact_category,))
                rows = cursor.fetchall()

                if rows:
                    lines = [f"- {row[0]} → {row[1]}" for row in rows]
                    result = "\n".join(lines)
                    message = f"📞 [{matched_contact_category}] 연락처 세부항목 목록입니다:\n{result}"
                else:
                    message = "해당 구분에 연락처 세부항목이 없습니다."

                final_msg = translator.translate(message, src='ko', dest=detected_lang).text if detected_lang != 'ko' else message
                dispatcher.utter_message(text=final_msg)
                return []

            # ------------------- 연락처 세부항목 직접 매칭 -------------------
            query = "SELECT `세부항목`, `상세내용` FROM number"
            cursor.execute(query)
            all_sub_items = cursor.fetchall()

            matched_sub_item = None
            for sub_item, detail in all_sub_items:
                if sub_item in translated_msg or translated_msg in sub_item:
                    matched_sub_item = (sub_item, detail)
                    break

            if matched_sub_item:
                sub_name, sub_detail = matched_sub_item
                message = f"{sub_detail}"
                final_msg = translator.translate(message, src='ko', dest=detected_lang).text if detected_lang != 'ko' else message
                dispatcher.utter_message(text=final_msg)
                return []

            # ------------------- 처리 실패 시 -------------------
            message = "죄송해요. 해당 내용을 이해하지 못했어요. 다시 질문해 주세요."
            final_msg = translator.translate(message, src='ko', dest=detected_lang).text if detected_lang != 'ko' else message
            dispatcher.utter_message(text=final_msg)
            return []

        finally:
            cursor.close()
            conn.close()