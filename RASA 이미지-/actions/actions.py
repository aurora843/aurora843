import pymysql
pymysql.install_as_MySQLdb()
from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher

class ActionShowCleaningImage(Action):
    def name(self):
        return "action_show_cleaning_image"

    def run(self, dispatcher, tracker, domain):
        conn = pymysql.connect(
            host='localhost',
            user='rasauser',
            password='rasa1234',
            db='rasa',
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
            user='rasauser',
            password='rasa1234',
            db='rasa',
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
