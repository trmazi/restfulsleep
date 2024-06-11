from flask_restful import Resource
from flask import request

from api.constants import APIConstants
from api.data.endpoints.arcade import ArcadeData
from api.data.endpoints.machine import MachineData
from api.data.endpoints.paseli import PaseliData
from api.data.endpoints.user import UserData
from api.data.endpoints.session import SessionData

class Arcades(Resource):
    '''
    Handle loading, creation, and updating of an arcade.
    Requires a valid user session and that a user owns an arcade.
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

        if not ArcadeData.checkOwnership(userId, arcadeId):
            return APIConstants.bad_end('You don\'t own this arcade or it doesn\'t exist!')
        
        arcade = ArcadeData.getArcade(arcadeId)
        if not arcade:
            return APIConstants.bad_end('Unable to load the arcade!')
        
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
        
        return {'status': 'success', 'arcade': arcade}
    
class Paseli(Resource):
    '''
    Handle loading and updating of PASELI information.
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

        if not ArcadeData.checkOwnership(userId, arcadeId):
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