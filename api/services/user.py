from flask_restful import Resource

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.card import CardCipher
from api.data.endpoints.arcade import ArcadeData
from api.data.endpoints.user import UserData
from api.data.endpoints.game import GameData

class getUserAccount(Resource):
    '''
    Given a user ID, return a user's public info.
    '''
    def get(self, userId):
        user = UserData.getUser(int(userId))
        if not user:
            return APIConstants.bad_end('No user found.')

        authUser = False;
        sessionState, session = RequestPreCheck.getSession()
        if sessionState:
            if user.get('id', 0) == session.get('id', -1):
                authUser = True

        userData = user.get('data', {})
        discordLink = userData.get('discord', {})
        avatar = None
        if discordLink.get('linked', False):
            avatar = f"https://cdn.discordapp.com/avatars/{discordLink.get('id')}/{discordLink.get('avatar')}"

        profiles = GameData.getUserGameSettings(userId)

        arcades = []
        if authUser:
            for arcade in ArcadeData.getUserArcades(userId):
                arcades.append({
                    'id': arcade,
                    'name': ArcadeData.getArcadeName(arcade)
                })

        return {
            'status': 'success',
            'user': {
                'id': user['id'],
                'name': user['username'],
                'email': user['email'] if authUser else None,
                'admin': user['admin'],
                'banned': user['banned'],
                'avatar': avatar,
                'data': user['data'] if authUser else None,
                'profiles': profiles,
                'arcades': arcades
            }
        }
    
class userCards(Resource):
    '''
    Handle loading, creation, and deletion of a user's cards. Requires the auth header for a user.
    '''
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        userId = session.get('id', 0)

        cards = UserData.getCards(int(userId))
        if not cards:
            return APIConstants.bad_end('No cards found.')
        
        returnCards = []
        for card in cards:
            returnCards.append({
                'id': card,
                'encoded': CardCipher.encode(card)
            })

        return {
            'status': 'success',
            'cards': returnCards
        }
