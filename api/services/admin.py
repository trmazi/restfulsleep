import requests
from flask_restful import Resource

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.admin import AdminData
from api.data.endpoints.arcade import ArcadeData
from api.data.endpoints.machine import MachineData
from api.external.badmaniac import BadManiac

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
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
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

            memberData = BadManiac.getDiscordMember(discordId)
            if not memberData:
                return APIConstants.bad_end(f'Failed to get user\'s Discord account.')

            formattedArcade['description'] = f"{memberData['username']}'s Arcade"
            
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
    
class Maintenance(Resource):
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        audit = AdminData.getRecentAuditEvents(40, 'maintenance')
        return {'status': 'success', 'data': audit}
    
    def post(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
        endTimestamp = data.get('endTimestamp', None)
        if not endTimestamp:
            return APIConstants.bad_end('No endTimestamp!')
        formattedEnd = (int(endTimestamp / 1000))

        try:
            AdminData.putAuditEvent('maintenance', session.get('id', 0), None, {'endTimestamp': formattedEnd, 'reason': data.get('reason', '')})
        except Exception as e:
            return APIConstants.bad_end(str(e))

        return {'status': 'success'}