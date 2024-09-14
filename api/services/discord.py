import requests
from io import BytesIO
from flask_restful import Resource
from flask import request, Response

from api.constants import APIConstants
from api.data.endpoints.arcade import ArcadeData
from api.data.endpoints.user import UserData
from api.data.endpoints.session import SessionData
from api.data.endpoints.pfsense import PFSenseData

class OnboardingVPN(Resource):
    '''
    Handle exporting of an arcade's VPN profile and send it to a Discord User.
    Requires a valid user session and that a user is an admin.
    '''
    def get(self, arcadeId: int):
        userAuthCode = request.headers.get('User-Auth-Key')
        if not userAuthCode:
            return APIConstants.bad_end('No user auth provided!')
        
        decryptedSession = None
        try:
            decryptedSession = SessionData.AES.decrypt(userAuthCode)
        except:
            return APIConstants.bad_end('Unable to decrypt SessionId!')
        if not decryptedSession:
            return APIConstants.bad_end('Unable to decrypt SessionId!')

        session = SessionData.checkSession(decryptedSession)
        if session.get('active') != True:
            return APIConstants.bad_end('Invalid user session!')
        
        userId = session.get('id', 0)
        user = UserData.getUser(userId)
        if not user.get("admin", False):
            return APIConstants.bad_end('You are not an admin!')
        
        arcade = ArcadeData.getArcade(arcadeId)
        if not arcade:
            return APIConstants.bad_end('Unable to load the arcade!')

        arcadeConfig = PFSenseData.export_vpn_profile(arcade)
        
        if arcadeConfig:
            discordId = request.args.get('discordId')
            if not discordId:
                return APIConstants.bad_end('No Discord ID!')

            file_content = str(arcadeConfig[0]).encode('utf-8')
            file_name = f"gradius-{arcadeConfig[1]}-phaseii-config.ovpn"

            files = {
                'vpnFile': (file_name, BytesIO(file_content), 'text/plain')
            }

            api_endpoint = f"http://10.5.7.20:8017/sendVPNProfile/{discordId}"

            try:
                response = requests.post(api_endpoint, files=files)

                if response.status_code == 200:
                    return {'status': 'success'}
                else:
                    return APIConstants.bad_end(f"Failed to upload file. Status code: {response.status_code}")
            
            except requests.RequestException as e:
                return APIConstants.bad_end(f"Error during upload: {str(e)}")
        
        else:
            return APIConstants.bad_end('Failed to export!')