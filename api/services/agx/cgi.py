from typing import Dict, Any
from flask_restful import Resource
from flask import Response
from api.data.time import Time
import json
import hashlib

class AGXServer:
    MARKER_URL = None
    MAGIC_KEY = None
    VERSION = "3.7.0"

    @staticmethod
    def updateConfig(agx_config: Dict[str, Any]) -> None:
        AGXServer.MARKER_URL = agx_config.get('marker-url', '')
        AGXServer.MAGIC_KEY = agx_config.get('magic-key', '')

        assert len(AGXServer.MAGIC_KEY) == 64

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
        markerData = []
        for i in range(1, 36):  # tm0001 to tm0035
            markerId = f"tm{i:04d}"
            markerName = f"mk{i:04d}"
            itemURL = f"{AGXServer.MARKER_URL}/{markerName}.zip"
            markerData.append({
                "ID": markerId,
                "Version": AGXServer.VERSION,
                "ItemURL": itemURL
            })
        response_dict = {
            "List": markerData
        }

        dumpedJSON = json.dumps(response_dict, separators=(',', ':')).encode('utf-8')
        digest = hashlib.sha256(AGXServer.MAGIC_KEY.encode('utf-8') + dumpedJSON).digest()
        hash = digest.hex()
        payload = hash.encode('utf-8') + dumpedJSON
        return Response(payload, mimetype='application/octet-stream')
    
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