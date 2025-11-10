from flask_restful import Resource

class APRSearchMaster(Resource):
    def get(self):
        return {
            "Version": "2.0.0",
            "Info": "https://i.redd.it/iqd154wkuy441.jpg",
            "Mark": [
                {
                    "Order": "0",
                    "Model": "TUNE STREET",
                    "Name": "Boss Battle Games",
                    "Image": "https://i.redd.it/iqd154wkuy441.jpg"
                }
            ],
            "GameCenterList": [
                {
                    "ID": 1,
                    "Lat": 39.9089,
                    "Long": -86.0652,
                    "Name": "Boss Battle Games",
                    "Open": "10:00-22:00",
                    "Model": ["1"]
                }
            ]
        }