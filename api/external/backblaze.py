from b2sdk.v2 import B2Api, InMemoryAccountInfo, AuthInfoCache
from typing import Dict, Any

class BackBlazeCDN:
    B2_API: B2Api = None
    bucket = None

    @staticmethod
    def update_config(bb_config: Dict[str, Any]) -> None:
        apiID = bb_config.get('key-id', '')
        apiKey = bb_config.get('auth-key', '')
        BackBlazeCDN.bucket = bb_config.get('bucket-name', '')

        info = InMemoryAccountInfo()
        BackBlazeCDN.B2_API = B2Api(info, cache=AuthInfoCache(info))
        BackBlazeCDN.B2_API.authorize_account("production", apiID, apiKey)

    def uploadUserVideo(self, videoData: bytes, sessionId: Any, videoId: Any):
        filepath = f'play-video/{str(sessionId)}.mp4'
        if self.B2_API:
            bucket = self.B2_API.get_bucket_by_name(self.bucket)
            bucket.upload_bytes(
                    data_bytes=videoData,
                    file_name=filepath,
                )
            return True
        else:
            return False
        
    def uploadUserContent(self, file: bytes, filepath: str):
        if self.B2_API:
            bucket = self.B2_API.get_bucket_by_name(self.bucket)
            bucket.upload_bytes(
                    data_bytes=file,
                    file_name=filepath,
                )
            return True
        else:
            return False