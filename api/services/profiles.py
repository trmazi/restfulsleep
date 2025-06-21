from flask_restful import Resource
from flask import request
import concurrent.futures

from api.constants import APIConstants, ValidatedDict
from api.precheck import RequestPreCheck
from api.data.endpoints.user import UserData
from api.data.endpoints.profiles import ProfileData
from api.data.endpoints.achievements import AchievementData
from api.data.endpoints.game import GameData
from api.data.cache import LocalCache

class allPlayers(Resource):
    def process_profile(self, profile, extIds, stats):
        userId = profile.get('userId')
        profile['stats'] = stats.get(userId)
        if profile['stats'] is None:
            return None
        profile['extid'] = extIds.get(userId)
        return profile

    def get(self, game: str):
        argsState, args = RequestPreCheck.checkArgs({
            'version': str
        })

        if argsState:
            try:
                version = int(args.get_str('version'))
            except:
                version = None
        
        cacheName = f'juiced_profiles_{game}'
        if not version:
            profileData = LocalCache().getCachedData(cacheName)
        else:
            profileData = None

        if not profileData:
            profileData = []
            profiles = ProfileData.getPlayers(game, version)
            extIds = {extid[0]: extid[1] for extid in GameData.getAllExtid(game)}
            stats = {stat[0]: stat[1] for stat in GameData.getAllGameStats(game)}

            with concurrent.futures.ProcessPoolExecutor() as executor:
                futures = {executor.submit(self.process_profile, profile, extIds, stats): profile for profile in profiles}
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result is not None:
                        profileData.append(result)

            if not version:
                LocalCache().putCachedData(cacheName, profileData)

        return {
            'status': 'success',
            'data': profileData
        }, 200

class Profile(Resource):
    def get(self, game: str):
        version = request.args.get('version')
        userId = request.args.get('userId')

        if not userId:
            return APIConstants.bad_end('No userId!')
        
        versions = ProfileData.getVersions(game, userId)
        if not version or version == 'null' and versions:
            version = versions[-1] if len(versions) > 1 else versions[0]

        profile = ProfileData.getProfile(game, version, userId)
        if not profile:
            return APIConstants.soft_end('No profile found!')
        
        profile['versions'] = versions
        profile['stats'] = GameData.getUserGameStats(game, userId)
        profile['extid'] = GameData.getUserExtid(game, userId)

        return {
            'status': 'success',
            'data': profile
        }, 200
    
    def post(self, game: str):
        session: ValidatedDict
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        version = request.args.get('version')
        userId = request.args.get('userId')

        if not userId:
            return APIConstants.bad_end('No userId!')

        sessionUserId = session.get_int('id', -1)
        sessionUser: ValidatedDict = UserData.getUser(sessionUserId)
        if not sessionUser:
            return APIConstants.bad_end('No user found.')
        
        if sessionUserId != int(userId):
            if not sessionUser.get_bool('admin'):
                return APIConstants.bad_end('This isn\'t your profile!')
        
        data = request.json
        if not data:
            return APIConstants.bad_end('No JSON data sent!')
        
        profile = ProfileData.getProfile(game, version, userId)
        if not profile:
            return APIConstants.soft_end('No profile found!')

        error_code = ProfileData.updateProfile(game, version, userId, data)
        if error_code:
            return APIConstants.bad_end(error_code)
        
        return {
            'status': 'success'
        }, 200
    
class Achievements(Resource):
    def get(self, game: str):
        args = ValidatedDict(request.args)

        version = int(args.get_str('version'))
        userId = int(args.get_str('userId'))
        header_value = request.headers.get('achievements', None)

        try:
            if header_value:
                achievements = [
                    (name, int(score)) for name, score in 
                    (item.split(':') for item in header_value.split(','))
                ]
            else:
                achievements = []
        except Exception as e:
            return APIConstants.bad_end(f'`achievements`: {e}')

        if not userId:
            return APIConstants.bad_end('No userId!')
        
        if not achievements:
            return APIConstants.bad_end('`achievements: list[str: int]` needs to be supplied in headers. The format is `achievementType:achievementId,`')
        
        versions = ProfileData.getVersions(game, userId)
        if not version or version == 'null' and versions:
            version = versions[-1] if len(versions) > 1 else versions[0]

        loadedAchievements = []
        try:
            for achievementType, achievementId in achievements:
                achievement = AchievementData.getAchievement(game, version, userId, achievementType, achievementId)
                loadedAchievements.append({
                    'achievementType': achievementType,
                    'achievementId': achievementId,
                    'data': achievement,
                })
        except:
            return APIConstants.bad_end('Failed to parse `achievements: list[str: int]` from headers')
        
        return {
            'status': 'success',
            'data': loadedAchievements
        }, 200