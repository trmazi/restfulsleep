from flask import request
from flask_restful import Resource

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.card import CardCipher
from api.data.endpoints.arcade import ArcadeData
from api.data.endpoints.user import UserData
from api.data.endpoints.profiles import ProfileData
from api.data.endpoints.game import GameData
from api.data.endpoints.score import ScoreData

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
    
    def put(self):
        '''
        Register a new user
        '''
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data

        username = None
        email = None
        newPassword = None
        confirmPassword = None
        pin = None
        cardId = None

        if data.get('username', None):
            try:
                username = str(data.get('username', None))
            except:
                return APIConstants.bad_end('Invalid username!')
            
            existingUser = UserData.getUserByName(username)
            if existingUser:
                return APIConstants.soft_end('Username already taken.')
        else:
            return APIConstants.bad_end('No username provided!')

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
        else:
            return APIConstants.bad_end('No email provided!')
            
        if data.get('newPassword', None):
            try:
                newPassword = str(data.get('newPassword', None))
            except:
                return APIConstants.bad_end('Invalid newPassword.')
        else:
            return APIConstants.bad_end('No newPassword provided!')
            
        if data.get('confirmPassword', None):
            try:
                confirmPassword = str(data.get('confirmPassword', None))
            except:
                return APIConstants.bad_end('Invalid confirmPassword.')
        else:
            return APIConstants.bad_end('No confirmPassword provided!')
        
        if len(str(newPassword)) < 8:
            return APIConstants.soft_end('Password must be at least 8 characters!')
        
        if newPassword != confirmPassword:
            return APIConstants.soft_end('The passwords don\'t match!')

        if data.get('pin', None):
            try:
                pin = str(data.get('pin', None))
            except:
                return APIConstants.bad_end('Invalid pin!')
            
            try:
                int(data.get('pin', None))
            except:
                return APIConstants.bad_end('Invalid pin!')
            
            if len(pin) != 4:
                return APIConstants.bad_end('PIN must be 4 characters!')
        else:
            return APIConstants.bad_end('No pin provided!')
        
        if data.get('cardId', None):
            try:
                cardId = str(data.get('cardId', None))
            except:
                return APIConstants.bad_end('Invalid cardId.')
        else:
            return APIConstants.bad_end('No cardId provided!')
        
        try:
            cardId = CardCipher.decode(cardId)
        except:
            return APIConstants.soft_end('Bad cardId encoding!')
        
        userId = UserData.cardExist(cardId)
        if not userId:
            return APIConstants.soft_end('Card is unused!\nPlease play a game to begin registration.')
        
        user = UserData.getUser(userId)
        if not user:
            return APIConstants.bad_end('No user found.')
        
        if user.get('username', None):
            return APIConstants.soft_end('User account is already claimed.')
        
        if not UserData.checkUserPin(userId, pin):
            return APIConstants.soft_end('PIN mismatch!')

        if not UserData.updateUser(userId, username, email, pin):
            return APIConstants.bad_end('Failed to update user.')
        
        if not UserData.updatePassword(userId, newPassword):
            return APIConstants.bad_end('Failed to update password!')

        return {'status': 'success'}

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
    
class UserCard(Resource):
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
    
    def post(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
        cardId = data.get('cardId', None)
        if cardId == None:
            return APIConstants.bad_end('No cardId provided.')
        
        try:
            cardId = CardCipher.decode(cardId)
        except:
            return APIConstants.soft_end('Bad encoding!')
        
        if UserData.cardExist(cardId):
            return APIConstants.soft_end('Card in use!')
        
        userId = session.get('id', 0)
        if not UserData.putCard(userId, cardId):
            return APIConstants.bad_end('Failed to add!')
        
        return {'status': 'success'}
    
    def delete(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        dataState, data = RequestPreCheck.checkData()
        if not dataState:
            return data
        
        cardId = data.get('cardId', None)
        if cardId == None:
            return APIConstants.bad_end('No cardId provided.')
        
        try:
            cardId = CardCipher.decode(cardId)
        except:
            return APIConstants.soft_end('Bad encoding!')
        
        userId = session.get('id', 0)
        if not UserData.deleteCard(userId, cardId):
            return APIConstants.bad_end('Failed to delete!')
        
        return {'status': 'success'}
    
class UserTakeover(Resource):
    '''
    Claim an already used card. Transfers user data into account
    '''
    
    def get(self):
        '''
        Get account information, check if new card is actually unregistered.
        '''
        userId = None
        sessionState, session = RequestPreCheck.getSession()
        if sessionState:
            userId = session.get('id', None)

        if not userId:
            return APIConstants.bad_end('Bad session!')

        pin = None
        cardId = None

        if request.args.get('pin', None):
            try:
                pin = str(request.args.get('pin', None))
            except:
                return APIConstants.bad_end('Invalid pin!')
            
            try:
                int(request.args.get('pin', None))
            except:
                return APIConstants.bad_end('Invalid pin!')
            
            if len(pin) != 4:
                return APIConstants.bad_end('PIN must be 4 characters!')
        else:
            return APIConstants.bad_end('No pin provided!')
        
        if request.args.get('cardId', None):
            try:
                cardId = str(request.args.get('cardId', None))
            except:
                return APIConstants.bad_end('Invalid cardId.')
        else:
            return APIConstants.bad_end('No cardId provided!')
        
        try:
            cardId = CardCipher.decode(cardId)
        except:
            return APIConstants.soft_end('Bad cardId encoding!')

        user = UserData.getUser(userId)
        if not user:
            return APIConstants.bad_end('No user found.')
        
        claimUserId = UserData.cardExist(cardId)
        if not claimUserId:
            return APIConstants.soft_end('Card is unused!')
        
        claimUser = UserData.getUser(claimUserId)
        if not claimUser:
            return APIConstants.bad_end('No user found.')
        
        if claimUser.get('username', None):
            return APIConstants.soft_end('User account is already claimed.')
        
        if not UserData.checkUserPin(claimUserId, pin):
            return APIConstants.soft_end('PIN mismatch!')
        
        profiles = GameData.getUserGameSettings(claimUserId)

        return {'status': 'success', 'data': {'userId': claimUserId, 'profiles': profiles}}
    
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

        pin = None
        cardId = None

        if data.get('pin', None):
            try:
                pin = str(data.get('pin', None))
            except:
                return APIConstants.bad_end('Invalid pin!')
            
            try:
                int(data.get('pin', None))
            except:
                return APIConstants.bad_end('Invalid pin!')
            
            if len(pin) != 4:
                return APIConstants.bad_end('PIN must be 4 characters!')
        else:
            return APIConstants.bad_end('No pin provided!')
        
        if data.get('cardId', None):
            try:
                cardId = str(data.get('cardId', None))
            except:
                return APIConstants.bad_end('Invalid cardId.')
        else:
            return APIConstants.bad_end('No cardId provided!')
        
        try:
            cardId = CardCipher.decode(cardId)
        except:
            return APIConstants.soft_end('Bad cardId encoding!')
        
        if data.get('mergeSettings', None):
            try:
                mergeSettings = dict(data.get('mergeSettings'))
            except:
                return APIConstants.bad_end('Invalid merge data!')
        else:
            return APIConstants.bad_end('No mergeSettings provided!')
        
        claimUserId = UserData.cardExist(cardId)
        if not claimUserId:
            return APIConstants.soft_end('Card is unused!\nPlease play a game to begin registration.')
        
        user = UserData.getUser(claimUserId)
        if not user:
            return APIConstants.bad_end('No user found.')
        
        if user.get('username', None):
            return APIConstants.soft_end('User account is already claimed.')
        
        if not UserData.checkUserPin(claimUserId, pin):
            return APIConstants.soft_end('PIN mismatch!')
        
        recordsCount = 0
        for game in mergeSettings:
            if game == 'card':
               UserData.transferCard(claimUserId, userId, cardId)

            else:
                gameSettings = mergeSettings[game]
                if gameSettings.get('scores'):
                    try:
                        recordsCount += ScoreData.transferUserRecords(game, claimUserId, userId)
                    except Exception as e:
                        return APIConstants.bad_end("Failed to transfer scores")

        return {'status': 'success', 'count': recordsCount}

class UserPlayVideos(Resource):
    '''
    Handle loading, and deletion of a user's play videos. Requires the auth header for a user.
    '''
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        userId = session.get('id', 0)

        playVideos = UserData.getUserPlayVideos(int(userId))

        return {
            'status': 'success',
            'data': playVideos
        }
    
class UserContent(Resource):
    '''
    Handle loading, and deletion of a user's content. Requires the auth header for a user.
    '''
    def get(self):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        if request.args.get('type', None):
            try:
                contentType = str(request.args.get('type', None))
            except:
                return APIConstants.bad_end('Invalid type!')
        
        userId = session.get('id', 0)

        userContent = UserData.getAllUserContent(int(userId), contentType)

        return {
            'status': 'success',
            'data': userContent
        }