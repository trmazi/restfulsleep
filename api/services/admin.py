import requests
from flask_restful import Resource
from flask import request

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.admin import AdminData
from api.data.endpoints.arcade import ArcadeData
from api.data.endpoints.machine import MachineData

class AdminDashboard(Resource):
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        statistics = AdminData.getStats()
        audit = AdminData.getRecentAuditEvents(40)
        return {'status': 'success', 'data': {'statistics': statistics, 'audit': audit}}

class OnboardArcade(Resource):
    '''
    Used to onboard an arcade.
    '''
    def post(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        data = request.json
        if not data:
            return APIConstants.bad_end('No JSON data sent!')
        
        formattedArcade = {
            'name': str(data['name']),
            'description': str(data['description']),
            'pin': 57305730,
            'data': {
                'paseli_enabled': bool(data['paseli']),
                'paseli_infinite': bool(data['infinitePaseli']),
                'maint': bool(data['maintenance']),
                'hide_network': bool(data['incognito']),
                'is_beta': bool(data['betas']),
                'is_arcade': False,
            }
        }

        if bool(data['useDiscord']):
            discordId = int(data['discordId'])
            api_endpoint = f"http://10.5.7.20:8017/member/{discordId}"

            try:
                response = requests.get(api_endpoint)
                if response.status_code != 200:
                    return APIConstants.bad_end(f"Failed to onboard. Status code: {response.status_code}")
                
            except requests.RequestException as e:
                return APIConstants.bad_end(f"Error during onboard: {str(e)}")
            
            responseData = response.json()
            formattedArcade['description'] = f"{responseData['username']}'s Arcade"
            
        newArcade = ArcadeData.putArcade(None, formattedArcade)
        
        for newMachine in data.get('machineList', []):
            formattedMachine = {
                'name': newMachine['name'],
                'PCBID': newMachine['PCBID'],
                'port': None,
                'ota': newMachine['ota'],
                'data': {
                    'cabinet': newMachine['cabinet']
                }
            }
            MachineData.putMachine(None, newArcade.get('id'), formattedMachine)

        return {'status': 'success', 'arcadeId': newArcade.get('id')}