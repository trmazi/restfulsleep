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
    
class AdminArcades(Resource):
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        arcades = ArcadeData.getAllArcades()
        return {'status': 'success', 'data': arcades}
    
class AdminArcade(Resource):
    def post(self, arcadeId: int):
        '''
        Update an arcade's name and description
        '''
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
            'beta': bool(data['beta']),
        }
        
        error_code = ArcadeData.updateArcadeNameDesc(arcadeId, formattedArcade.get('name', ''), formattedArcade.get('description', ''), formattedArcade.get('beta', False))
        if error_code:
            return APIConstants.bad_end(error_code)
        
        return {
            'status': 'success'
        }, 200
    
class AdminArcadeOwner(Resource):
    def put(self, arcadeId: int):
        '''
        Add a new arcade owner
        '''
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
        success = ArcadeData.putArcadeOwner(arcadeId, data.get_int('ownerId'))
        if not success:
            return APIConstants.bad_end("Failed to add arcade owner!")
        
        return {
            'status': 'success'
        }, 200
    
    def delete(self, arcadeId: int):
        '''
        Remove an arcade owner
        '''
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
        success = ArcadeData.removeArcadeOwner(arcadeId, data.get_int('ownerId'))
        if not success:
            return APIConstants.bad_end("Failed to remove arcade owner!")
        
        return {
            'status': 'success'
        }, 200

class AdminArcadeMachine(Resource):
    def post(self, arcadeId: int):
        '''
        Create a new machine for an existing arcade
        '''
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
        formattedMachine = {
            'name': data['name'],
            'PCBID': data['PCBID'],
            'port': None,
            'ota': data['ota'],
            'data': {
                'cabinet': data['cabinet']
            }
        }
        
        machine = MachineData.putMachine(None, arcadeId, formattedMachine)
        if not machine:
            return APIConstants.bad_end('Failed to add machine')
        
        return {
            'status': 'success'
        }, 200

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
    
class Client(Resource):
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        audit = AdminData.getAllClients()
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
        
        name = data.get_str('name', None)
        if not name: 
            return APIConstants.bad_end('No name provided!')
        
        if not AdminData.putClient(name):
            return APIConstants.bad_end('Failed to put client!')
        
        audit = AdminData.getAllClients()
        return {'status': 'success', 'data': audit}

class AdminUsers(Resource):
    '''
    Handle loading user data for admin management
    '''
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode

        argsState, args = RequestPreCheck.checkArgs()
        if not argsState:
            return args
        
        noData = args.get('noData', False)
        try:
            noData = bool(noData)
        except:
            return APIConstants.bad_end('noData was provided but it isn\'t a bool!')
        
        users = AdminData.getAllUsers()
        return {'status': 'success', 'data': users}
    
class News(Resource):
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        news = AdminData.getAllNews()
        return {'status': 'success', 'data': news}
    
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
        
        title = data.get_str('title', None)
        if not title: 
            return APIConstants.bad_end('No title provided!')
        
        body = data.get_str('body', None)
        if not body: 
            return APIConstants.bad_end('No body provided!')
        
        data = data.get_dict('data', None)
        if not data: 
            return APIConstants.bad_end('No data provided!')
        
        if not AdminData.putNews(title, body, data):
            return APIConstants.bad_end('Failed to put news!')
        
        news = AdminData.getAllNews()
        return {'status': 'success', 'data': news}
