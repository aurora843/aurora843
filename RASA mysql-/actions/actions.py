import pymysql
from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher

class ActionShowMealInfo(Action):
    def name(self):
        return "action_show_meal_info"

    def run(self, dispatcher, tracker, domain):
        # MySQL 연결
        conn = pymysql.connect(
            host='localhost',
            user='rasauser',
            password='rasa1234',
            db='rasa',
            charset='utf8'
        )
        cursor = conn.cursor()

        # 급식 정보 가져오기
        cursor.execute("SELECT info_text FROM text_info WHERE info_type = 'meal'")
        result = cursor.fetchone()

        if result:
            dispatcher.utter_message(text=result[0])
        else:
            dispatcher.utter_message(text="급식 정보가 없습니다.")

        cursor.close()
        conn.close()
        return []

class ActionShowLaundryInfo(Action):
    def name(self):
        return "action_show_laundry_info"

    def run(self, dispatcher, tracker, domain):
        # MySQL 연결
        conn = pymysql.connect(
            host='localhost',
            user='rasauser',
            password='rasa1234',
            db='rasa',
            charset='utf8'
        )
        cursor = conn.cursor()

        # 세탁 정보 가져오기
        cursor.execute("SELECT info_text FROM text_info WHERE info_type = 'laundry'")
        result = cursor.fetchone()

        if result:
            dispatcher.utter_message(text=result[0])
        else:
            dispatcher.utter_message(text="세탁 정보가 없습니다.")

        cursor.close()
        conn.close()
        return []


