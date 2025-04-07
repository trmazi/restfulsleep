import requests
from typing import Dict, Any
from api.constants import APIConstants

class BadManiac:
    BM_URL = None
    BM_KEY = None

    @staticmethod
    def update_config(bm_config: Dict[str, Any]) -> None:
        BadManiac.BM_URL = bm_config.get('endpoint', '')
        BadManiac.BM_KEY = bm_config.get('auth-key', '')

    @staticmethod
    def send_link_complete(discord_id: str):
        request_data = {
            "discordId": discord_id,
        }
        try:
            requests.post(f"{BadManiac.BM_URL}/successfulLink", json=request_data, headers={"X-API-Key": BadManiac.BM_KEY})
        except:
            return APIConstants.bad_end('fuck')

    @staticmethod
    def send_upload_complete(discord_id: str, video_path: str, session_id: str):
        request_data = {
            "discordId": discord_id,
            "video": {
                "url": f"{video_path}/{session_id}.mp4",
            }
        }
        try:
            requests.post(f"{BadManiac.BM_URL}/uploadComplete", json=request_data, headers={"X-API-Key": BadManiac.BM_KEY})
        except:
            return APIConstants.bad_end('fuck')