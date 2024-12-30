from flask_restful import Resource
from flask import Response, request

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.arcade import ArcadeData
from api.data.endpoints.machine import MachineData
from api.data.endpoints.paseli import PaseliData
from api.data.endpoints.user import UserData
from api.data.endpoints.pfsense import PFSenseData

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
            return {'status': 'success', 'data': arcade_settings}
        
        return APIConstants.bad_end('Unauthorized.')
    
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

        arcade_config = PFSenseData.export_vpn_profile(arcade)
        
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