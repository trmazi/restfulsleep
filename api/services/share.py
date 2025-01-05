import requests
from typing import Any, Dict
from flask_restful import Resource
from flask import request

from api.data.endpoints.share import ShareData
from api.data.endpoints.user import UserData
from api.external.backblaze import BackBlazeCDN
from api.external.badmaniac import BadManiac

class ShareServer:
    SERVER_ENDPOINT = None
    PUBLIC_PATH = None

    @staticmethod
    def update_config(share_config: Dict[str, Any]) -> None:
        ShareServer.SERVER_ENDPOINT = share_config.get('upload-endpoint', '')
        ShareServer.PUBLIC_PATH = share_config.get('public-path', '')

class shareServerStatus(Resource):
    def get(self):
        response_data = {
            "status": 200,
            "message": ""
        }
        return response_data, 200

class shareNewSession(Resource):
    def post(self):
        session_id = ShareData.getNextSession()
        response_data = {
            "status": 200,
            "message": "",
            "session": session_id
        }
        return response_data, 200

class shareBeginUpload(Resource):
    def post(self, session_id, video_id):
        upload_endpoint = ShareServer.SERVER_ENDPOINT

        if upload_endpoint:
            response_data = {
                "status": 200,
                "message": "",
                "url": f'{upload_endpoint}/share/videoUpload/{session_id}/{video_id}'
            }
        else: 
            response_data = {
                "status": 500,
                "message": "Share server not ready!",
                "url": ""
            }

        return response_data, 200
    
class shareVideoUpload(Resource):
    def put(self, session_id, video_id):
        if request.data:
            uploadState = BackBlazeCDN().uploadUserVideo(request.data, session_id, video_id)
            if uploadState:
                return 200

        return 500

class shareEndUpload(Resource):
    def post(self, session_id, video_id):
        public_path = ShareServer.PUBLIC_PATH
        update_status = UserData.updateUserPlayVideoData(session_id, {"status": "uploaded", "url": f"{public_path}/{session_id}.mp4"})

        video = UserData.getUserPlayVideo(session_id)
        user = UserData.getUser(video.get('userid', 0))

        userDiscord = user.get('data', {}).get('discord', {})
        if userDiscord.get('linked', False):
            BadManiac.send_upload_complete(userDiscord.get('id'), public_path, session_id)

        if not update_status:
            response_data = {
                "status": 200,
                "message": ""
            }
        else:
            response_data = {
                "status": 500,
                "message": ""
            }
        return response_data, 200