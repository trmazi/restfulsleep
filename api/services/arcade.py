from flask_restful import Resource
from flask import Response, request

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.arcade import ArcadeData
from api.data.endpoints.machine import MachineData
from api.data.endpoints.paseli import PaseliData
from api.data.endpoints.user import UserData
from api.external.pfsense import PFSense

class Arcades(Resource):
    '''
    Handle loading, creation, and updating of an arcade.
    Requires a valid user session and that a user owns an arcade (or if user is admin).
    '''
    def get(self, arcadeId: int):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        userId = session.get('id', 0)
        user = UserData.getUser(userId)
        authUser = True

        if not ArcadeData.checkOwnership(userId, arcadeId) and not user.get("admin", False):
            authUser = False
        
        arcade = ArcadeData.getArcade(arcadeId)
        if not arcade:
            return APIConstants.bad_end('Unable to load the arcade!')
        
        if authUser:
            filteredOwners = []
            owners = ArcadeData.getArcadeOwners(arcadeId)
            for owner in owners:
                ownerData = UserData.getUser(owner)
                if ownerData is not None:
                    data = ownerData.get('data', {})
                    discordLink = data.get('discord', {})
                    avatar = None
                    if discordLink.get('linked', False):
                        avatar = f"https://cdn.discordapp.com/avatars/{discordLink.get('id')}/{discordLink.get('avatar')}"


                    ownerData['email'] = None
                    ownerData['data'] = None
                    ownerData['avatar'] = avatar
                    filteredOwners.append(ownerData)

            arcade['owners'] = filteredOwners
            arcade['machines'] = MachineData.getArcadeMachines(arcadeId)
        
        return {'status': 'success', 'arcade': arcade if authUser else {'name': arcade.get('name'), 'description': arcade.get('description')}}
    
    def post(self, arcadeId: int):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        userId = session.get('id', 0)
        user = UserData.getUser(userId)

        if not ArcadeData.checkOwnership(userId, arcadeId) and not user.get("admin", False):
            return APIConstants.bad_end('You don\'t have access to this arcade!')
        
        arcade = ArcadeData.getArcade(arcadeId)
        if not arcade:
            return APIConstants.bad_end('Unable to load the arcade!')
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data

        error_code = ArcadeData.updateArcadeData(arcadeId, data)
        if error_code:
            return APIConstants.bad_end(error_code)
        
        return {
            'status': 'success'
        }, 200
    
class ArcadeSettings(Resource):
    '''
    Handle loading, creation, and updating of game event settings for an arcade.
    Requires a valid user session and that a user owns an arcade (or if user is admin) for updating.
    '''
    def get(self, arcadeId: int):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        userId = session.get('id', 0)
        user = UserData.getUser(userId)
        authUser = True

        if not ArcadeData.checkOwnership(userId, arcadeId) and not user.get("admin", False):
            authUser = False
        
        arcade = ArcadeData.getArcade(arcadeId)
        if not arcade:
            return APIConstants.bad_end('Unable to load the arcade!')
        
        game = request.args.get('game')
        try:
            game = str(game)
        except:
            return APIConstants.bad_end('Game is malformed!')
        
        version = request.args.get('version')
        try:
            version = int(version)
        except:
            return APIConstants.bad_end('Version is malformed!')
        
        if authUser:
            arcade_settings = ArcadeData.getArcadeSettings(arcadeId, game, version, 'game_config')
            return {'status': 'success', 'data': arcade_settings if arcade_settings else {}}
        
        return APIConstants.bad_end('Unauthorized.')
    
    def post(self, arcadeId: int):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        userId = session.get('id', 0)
        user = UserData.getUser(userId)

        if not ArcadeData.checkOwnership(userId, arcadeId) and not user.get("admin", False):
            return APIConstants.bad_end('Unauthorized.')
        
        arcade = ArcadeData.getArcade(arcadeId)
        if not arcade:
            return APIConstants.bad_end('Unable to load the arcade!')
        
        game = request.args.get('game')
        try:
            game = str(game)
        except:
            return APIConstants.bad_end('Game is malformed!')
        
        version = request.args.get('version')
        try:
            version = int(version)
        except:
            return APIConstants.bad_end('Version is malformed!')
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data

        update_state = ArcadeData.updateArcadeSettings(arcadeId, game, version, 'game_config', data)
        if update_state:
            return APIConstants.bad_end(update_state)

        return {'status': 'success'}
    
class VPN(Resource):
    '''
    Handle exporting of an arcade's VPN profile.
    Requires a valid user session and that a user owns an arcade (or if user is admin).
    '''
    def get(self, arcadeId: int):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        userId = session.get('id', 0)
        user = UserData.getUser(userId)

        if not ArcadeData.checkOwnership(userId, arcadeId) and not user.get("admin", False):
            return APIConstants.bad_end('You don\'t own this arcade or it doesn\'t exist!')
        
        arcade = ArcadeData.getArcade(arcadeId)
        if not arcade:
            return APIConstants.bad_end('Unable to load the arcade!')

        arcade_config = PFSense.export_vpn_profile(arcade)
        
        if arcade_config:
            return Response(
                arcade_config[0],
                mimetype="text/plain",
                headers={"Content-Disposition": f"attachment;filename=gradius-{arcade_config[1]}-phaseii-config.ovpn"}
            )
        else:
            return APIConstants.bad_end('Failed to export!')
    
class Paseli(Resource):
    '''
    Handle loading and updating of PASELI information.
    '''
    def get(self, arcadeId: int):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        userId = session.get('id', 0)
        user = UserData.getUser(userId)

        if not ArcadeData.checkOwnership(userId, arcadeId) and not user.get("admin", False):
            return APIConstants.bad_end('You don\'t own this arcade or it doesn\'t exist!')
        
        returnData = {}
        balances = PaseliData.getArcadeBalances(arcadeId)
        filteredBalances = []
        if balances:
            for balance in balances:
                user = UserData.getUser(balance.get('userId', 0))
                filteredBalances.append({
                    'username': user.get('username'),
                    'balance': balance.get('balance', 0)
                })

        returnData['balances'] = filteredBalances

        returnData['transactions'] = []
        transactions = PaseliData.getTransactions(arcadeId)
        if transactions:
            returnData['transactions'] = transactions
        
        return {'status': 'success', 'data': returnData}
    
class CheckArcadeName(Resource):
    '''
    Check if an arcade name has been taken
    '''
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        name = request.args.get('name')
        if not name:
            return APIConstants.bad_end('No name provided!')
        
        validArcade = True
        if ArcadeData.fromName(name):
            validArcade = False
        
        return {'status': 'success', 'unused': validArcade}

class CheckPCBID(Resource):
    '''
    Check if PCBID has been taken
    '''
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        adminState, errorCode = RequestPreCheck.checkAdmin(session)
        if not adminState:
            return errorCode
        
        pcbid = request.args.get('PCBID')
        if not pcbid:
            return APIConstants.bad_end('No PCBID provided!')
        
        if len(pcbid) != 20:
            return APIConstants.bad_end('PCBID must be 20 characters!')
        
        validArcade = True
        if MachineData.fromPCBID(pcbid):
            validArcade = False
        
        return {'status': 'success', 'unused': validArcade}
    
class ArcadeTakeover(Resource):
    '''
    Claim an already used card. Transfers arcade perms into account
    '''
    
    def get(self):
        '''
        Get arcade information, check if arcade is actually unregistered.
        '''
        userId = None
        sessionState, session = RequestPreCheck.getSession()
        if sessionState:
            userId = session.get('id', None)

        if not userId:
            return APIConstants.bad_end('Bad session!')

        PCBID = None

        if request.args.get('PCBID', None):
            try:
                PCBID = str(request.args.get('PCBID', None))
            except:
                return APIConstants.bad_end('Invalid PCBID!')
        else:
            return APIConstants.bad_end('No PCBID provided!')
        
        machine = MachineData.fromPCBID(PCBID)
        if not machine:
            return APIConstants.bad_end('No machine found!')

        owners = ArcadeData.getArcadeOwners(machine.get('arcadeId', 0))
        if owners:
            return APIConstants.bad_end('Arcade already claimed!')
        
        if len(owners) != 0:
            return APIConstants.bad_end('Arcade already claimed!')

        arcade = ArcadeData.getArcade(machine.get('arcadeId', 0))
        machines = MachineData.getArcadeMachines(machine.get('arcadeId', 0))

        return {'status': 'success', 'data': {'arcade': arcade, 'count': len(machines)}}
    
    def post(self):
        '''
        Claim an already used card. Transfers user data into account
        '''
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
        userId = None
        sessionState, session = RequestPreCheck.getSession()
        if sessionState:
            userId = session.get('id', None)

        if not userId:
            return APIConstants.bad_end('Bad session!')

        PCBID = None

        if data.get('PCBID', None):
            try:
                PCBID = str(data.get('PCBID', None))
            except:
                return APIConstants.bad_end('Invalid PCBID!')
            
            if len(PCBID) != 20:
                return APIConstants.bad_end('PCBID must be 20 characters!')
        else:
            return APIConstants.bad_end('No PCBID provided!')
        
        machine = MachineData.fromPCBID(PCBID)
        if not machine:
            return APIConstants.bad_end('No machine found!')

        owners = ArcadeData.getArcadeOwners(machine.get('arcadeId', 0))
        if owners:
            return APIConstants.bad_end('Arcade already claimed!')
        
        if len(owners) != 0:
            return APIConstants.bad_end('Arcade already claimed!')

        saveState = ArcadeData.putArcadeOwner(machine.get('arcadeId', 0), userId)
        if not saveState:
            return APIConstants.bad_end('Failed to transfer arcade.')

        return {'status': 'success'}