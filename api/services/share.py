import requests
from typing import Any, Dict
from flask_restful import Resource
from flask import request

from api.data.endpoints.share import ShareData
from api.data.endpoints.user import UserData
from api.external.backblaze import BackBlazeCDN

class ShareServer:
    SERVER_ENDPOINT = None
    PUBLIC_PATH = None

    @staticmethod
    def update_config(share_config: Dict[str, Any]) -> None:
        ShareServer.SERVER_ENDPOINT = share_config.get('upload-endpoint', '')
        ShareServer.PUBLIC_PATH = share_config.get('public-path', '')

class shareServerStatus(Resource):
    def get(self):
        responseData = {
            "status": 200,
            "message": ""
        }
        return responseData, 200

class shareNewSession(Resource):
    def post(self):
        sessionId = ShareData.getNextSession()
        responseData = {
            "status": 200,
            "message": "",
            "session": sessionId
        }
        return responseData, 200

class shareBeginUpload(Resource):
    def post(self, sessionId, videoId):
        upload_endpoint = ShareServer.SERVER_ENDPOINT

        if upload_endpoint:
            responseData = {
                "status": 200,
                "message": "",
                "url": f'{upload_endpoint}/share/videoUpload/{sessionId}/{videoId}'
            }
        else: 
            responseData = {
                "status": 500,
                "message": "Share server not ready!",
                "url": ""
            }

        return responseData, 200
    
class shareVideoUpload(Resource):
    def put(self, sessionId, videoId):
        if request.data:
            uploadState = BackBlazeCDN().uploadUserVideo(request.data, sessionId, videoId)
            if uploadState:
                return 200

        return 500

class shareEndUpload(Resource):
    def post(self, sessionId, videoId):
        public_path = ShareServer.PUBLIC_PATH
        update_status = UserData.updateUserPlayVideoData(sessionId, {"status": "uploaded", "url": f"{public_path}/{sessionId}.mp4"})

        video = UserData.getUserPlayVideo(sessionId)
        user = UserData.getUser(video.userid)

        userDiscord = user.get('data', {}).get('discord', {})
        if userDiscord.get('linked', False):
            request_data = {
                "discordId": userDiscord.get('id', None),
                "video": {
                    "url": f"{public_path}/{sessionId}.mp4",
                }
            }
            api_endpoint = f"http://10.5.7.20:8017/uploadComplete"
            try:
                requests.post(api_endpoint, json=request_data)
            except:
                return None, 500

        if not update_status:
            responseData = {
                "status": 200,
                "message": ""
            }
        else:
            responseData = {
                "status": 500,
                "message": ""
            }
        return responseData, 200