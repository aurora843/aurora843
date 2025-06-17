import mysql.connector
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
import difflib
from googletrans import Translator # 설치 필요: pip install googletrans==4.0.0-rc1

# --- DB 접속 정보 (한 곳에서 관리) ---
# 중요: 실제 운영 시에는 환경 변수 등으로 안전하게 관리하세요
DB_CONFIG = {
    'host': 'database-1.cpe6wsy0uzhp.ap-northeast-2.rds.amazonaws.com', # 당신의 RDS Endpoint
    'user': 'root',
    'password': '12345678', # 본인 DB 비밀번호로 설정
    'database': 'rasa_core'
}

# --- 이미지 서버 기본 URL (여기서 수정) ---
# Nginx가 당신의 도메인을 통해 이미지를 서빙하도록 설정되어 있습니다.
# 이미지가 /var/www/html/images/ 디렉토리에 있고, Nginx가 이를 서빙한다면
# http://rasa-chatbot.shop/images 를 사용해야 합니다.
IMAGE_SERVER_URL = "http://rasa-chatbot.shop/images" # <--- 이 부분을 수정했습니다.

# --- 액션 1: 연락처 및 규칙 '텍스트' 정보 처리 ---
class ActionChatBot(Action):
    def name(self) -> Text:
        return "action_chatbot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        original_message = tracker.latest_message.get('text')
        if not original_message:
            return []
            
        translator = Translator()

        # --- 언어 감지 및 번역 ---
        detected_lang = 'ko'
        translated_msg = original_message
        try:
            if original_message: 
                detected = translator.detect(original_message)
                if detected:
                    detected_lang = detected.lang
                    if detected_lang != 'ko':
                        translated_msg = translator.translate(original_message, src=detected_lang, dest='ko').text
        except Exception as e:
            print(f"번역 오류: {e}")

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # --- 규칙 카테고리 판별 (키워드 기반) ---
            # 규칙 카테고리 이름과 이미지 ID 매핑
            rule_category_map = {
                "일반 규칙": 1, "기숙사 시설 이용": 2, "주의사항 (화재)": 3,
                "주의사항 (화상)": 4, "기타 주의사항": 5, "금지 행위": 6,
                "상벌 제도": 7, "세탁 카페": 8, "버스 시간표": 9
            }
            
            determined_rule_category = None
            for category_name in rule_category_map.keys():
                main_keyword = category_name.split(' ')[0]
                if category_name in translated_msg or main_keyword in translated_msg:
                    determined_rule_category = category_name
                    break

            # --- 규칙 세부 내용 + 이미지 출력 ---
            if determined_rule_category:
                message_text = ""
                image_url_to_send = None

                # 1. 이미지 URL 생성
                # rule_category_map의 값(이미지 ID)을 파일명으로 사용한다고 가정합니다.
                # 예: IMAGE_SERVER_URL/1.png
                image_id = rule_category_map.get(determined_rule_category)
                if image_id:
                    # 이미지 파일 확장자 지정 (예: .png 또는 .jpg)
                    # 실제 이미지 파일명 규칙에 따라 조정하세요.
                    image_url_to_send = f"{IMAGE_SERVER_URL}/{image_id}.png" # <--- 파일 확장자 추가 (예: .png)

                # 2. 규칙 텍스트 설명 조회 (rules_data 테이블에서)
                query_text = "SELECT sub_category, details FROM rules_data WHERE category = %s"
                cursor.execute(query_text, (determined_rule_category,))
                rows_text = cursor.fetchall()

                if rows_text:
                    lines = [f"- {row[0]}: {row[1]}" for row in rows_text]
                    result = "\n".join(lines)
                    message_text = f"📚 **[{determined_rule_category}]** 안내입니다.\n\n{result}"
                else: 
                    message_text = f"📚 **[{determined_rule_category}]** 관련 정보입니다."
                
                # 3. 메시지 번역 및 전송 (텍스트와 이미지 함께)
                final_msg = translator.translate(message_text, src='ko', dest=detected_lang).text if detected_lang != 'ko' else message_text
                dispatcher.utter_message(text=final_msg, image=image_url_to_send)
                return []

            # --- 연락처 관련 로직 (위에서 규칙으로 처리되지 않았을 경우 실행) ---
            # (연락처 조회 로직은 여기에 위치시킵니다. 여기서는 예시로 '연락처 목록'만 남겨둡니다.)
            if "연락처 목록" in translated_msg or "연락처 카테고리" in translated_msg:
                query = "SELECT DISTINCT category FROM chatbot"
                cursor.execute(query)
                rows = cursor.fetchall()
                message = "연락처 카테고리가 등록되어 있지 않습니다."
                if rows:
                    categories = [row[0] for row in rows]
                    result = "\n- " + "\n- ".join(categories)
                    message = f"📞 현재 등록된 연락처 카테고리는 다음과 같습니다:\n{result}"
                
                final_msg = translator.translate(message, src='ko', dest=detected_lang).text if detected_lang != 'ko' else message
                dispatcher.utter_message(text=final_msg)
                return []

            # (다른 연락처 조회 로직도 이 부분에 추가할 수 있습니다.)

            # --- 처리 실패 시 (Fallback) ---
            fallback_message = "죄송해요. 해당 내용을 이해하지 못했어요. 다시 질문해 주세요."
            final_fallback_msg = translator.translate(fallback_message, src='ko', dest=detected_lang).text if detected_lang != 'ko' else fallback_message
            dispatcher.utter_message(text=final_fallback_msg)
            return []

        except Exception as e:
            print(f"actions.py 오류: {e}")
            dispatcher.utter_message(text="죄송합니다. 요청을 처리하는 중 오류가 발생했습니다.")
            return []
        finally:
            if conn and conn.is_connected():
                if cursor: cursor.close()
                conn.close()


# --- 액션 2: 수강신청/건물위치 이미지 출력 전용 ---
class ActionShowImage(Action):
    def name(self) -> Text:
        return "action_show_image"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent_name = tracker.latest_message['intent'].get('name')

        # 이미지 파일 확장자 지정 (예: .png 또는 .jpg)
        # 실제 이미지 파일명 규칙에 따라 조정하세요.
        # 예시로 .png를 사용했지만, 실제 파일 확장자에 따라 변경해야 합니다.
        if intent_name == "ask_course_registration":
            dispatcher.utter_message(response="utter_course_registration_info")
            course_image_ids = [101, 102]
            for image_id in course_image_ids:
                dispatcher.utter_message(image=f"{IMAGE_SERVER_URL}/{image_id}.png") # <--- 파일 확장자 추가
            return [] # 액션 처리가 끝나면 바로 반환

        elif intent_name == "ask_building_location":
            dispatcher.utter_message(response="utter_school_map_info")
            map_image_id = 103 
            dispatcher.utter_message(image=f"{IMAGE_SERVER_URL}/{map_image_id}.png") # <--- 파일 확장자 추가
            return [] # 액션 처리가 끝나면 바로 반환
            
        # 만약 intent_name이 위 조건에 해당하지 않을 경우 (선택 사항)
        dispatcher.utter_message(text="요청하신 이미지 정보를 찾을 수 없습니다.")
        return []
