from flask import request
from flask_restful import Resource

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.card import CardCipher
from api.data.endpoints.arcade import ArcadeData
from api.data.endpoints.user import UserData
from api.data.endpoints.game import GameData

class UserAccount(Resource):
    def get(self):
        '''
        Loads a user's account based on ID or a User Auth Key.
        If given a user ID, only return a user's public info. Otherwise, return everything.
        '''
        userId = request.args.get('userId')
        if not userId:
            return APIConstants.bad_end('No userId provided')

        user = UserData.getUser(int(userId))
        if not user:
            return APIConstants.bad_end('No user found.')

        authUser = False;
        sessionState, session = RequestPreCheck.getSession()
        if sessionState:
            if user.get('id', 0) == session.get('id', -1):
                if user.get('banned', False):
                    return APIConstants.bad_end('You have been banned.')
                authUser = True

        if user.get('banned', False):
            return APIConstants.bad_end('This user is banned.')

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
    
    def post(self):
        '''
        Given new user params, save them.
        '''
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
        userId = session.get('id', 0)
        username = None
        email = None
        pin = None

        if data.get('username', None):
            try:
                username = str(data.get('username', None))
            except:
                return APIConstants.bad_end('Invalid username!')
            
            existingUser = UserData.getUserByName(username)
            if existingUser and existingUser.get('id') != userId:
                return APIConstants.bad_end('Username already taken.')

        if data.get('email', None):
            try:
                email = str(data.get('email', None))
            except:
                return APIConstants.bad_end('Invalid email!')

            splitEmail = email.split('@')
            if len(splitEmail) != 2:
                return APIConstants.bad_end('Invalid email!')
            
            if len(splitEmail[1].split('.')) != 2:
                return APIConstants.bad_end('Invalid email!')

        if data.get('pin', None):
            try:
                pin = str(data.get('pin', None))
            except:
                return APIConstants.bad_end('Invalid pin!')
            
            if len(pin) != 4 and len(pin) != 0:
                return APIConstants.bad_end('PIN must be 4 characters!')
            
            if len(pin) == 0:
                pin = None # If it's an empty string, we'll just forget it.
            
        if UserData.updateUser(userId, username, email, pin):
            return {'status': 'success'}

        return APIConstants.bad_end('Failed to save!')

class UserUpdatePassword(Resource):
    def post(self):
        '''
        Validate user, changes password.
        '''
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
        userId = session.get('id', 0)

        currentPassword = data.get('currentPassword', None)
        if currentPassword == None:
            return APIConstants.bad_end('No currentPassword provided.')
        
        if not UserData.validatePassword(currentPassword, userId):
            return APIConstants.soft_end('Password incorrect.')
        
        newPassword = data.get('newPassword', None)
        if newPassword == None:
            return APIConstants.bad_end('No newPassword provided.')
        
        confirmPassword = data.get('confirmPassword', None)
        if confirmPassword == None:
            return APIConstants.bad_end('No confirmPassword confirmation provided.')
        
        if len(str(newPassword)) < 8:
            return APIConstants.soft_end('Password must be at least 8 characters!')
        
        if newPassword != confirmPassword:
            return APIConstants.soft_end('The passwords don\'t match!')
        
        user = UserData.getUser(userId)
        if not user:
            return APIConstants.bad_end('No user found.')
        
        if user.get('banned', False):
            return APIConstants.bad_end('You\'re banned.')

        if UserData.updatePassword(user.get('id', 0), newPassword) == True:
            return {'status': 'success'}
        else:
            return APIConstants.bad_end('Failed to update password!')
    
class UserCards(Resource):
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
