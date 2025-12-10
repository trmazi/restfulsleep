from flask_restful import Resource

class AQQLabiOS(Resource):
    def get(self):
        return {
            "Status": 0,
            "URL": "https://jubeat-lab-game.ez4dj.com/aqq/contents/ios/index.jsp"
        }