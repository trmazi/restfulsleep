from flask_restful import Resource
from flask import request, Response
from api.data.time import Time
import plistlib

class AGXStartup(Resource):
    def get(self):
        now = Time.now()

        return {
            "Status": 1,
            "SvTime": Time.format(now, "%Y%m%d%H%M"),
            "AnotherURL": "https://jubeat-lab-game.ez4dj.com/?another",
            "UpdateTime": Time.format(now, "%Y%m%d%H%M"),
            "URL": "https://jubeat-lab-game.ez4dj.com/"
        }
    
class AGXCheckMarker(Resource):
    def get(self):
        markerList = range(1, 36)
        markerData = [{"ID": marker, "Version": "3.7.0"} for marker in markerList]
        data =  {
            "List": markerData
        }

        plist = plistlib.dumps(data, fmt=plistlib.FMT_XML)
        print(plist)
        return Response(plist, mimetype="application/x-plist")
    
class AGXNew(Resource):
    def get(self):
        return {
            "UpdateTime": Time.format(Time.now(), "%Y%m%d%H%M"),
            "UpdateText": [
                "New update 1", "New update 2"
            ]
        }
    
class AGXPolicyStore(Resource):
    def get(self):
        return {
            "Status": 0,
            "URL": "https://jubeat-lab-game.ez4dj.com/ios"
        }