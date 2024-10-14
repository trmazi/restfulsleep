from flask_restful import Resource
from flask import request
import concurrent.futures

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.profiles import ProfileData
from api.data.endpoints.game import GameData

class allPlayers(Resource):
    def process_profile(self, profile, extIds, stats):
        userId = profile.get('userId')
        profile['stats'] = stats.get(userId)
        if profile['stats'] is None:
            return None
        profile['extid'] = extIds.get(userId)
        return profile

    def get(self, game: str):
        data = []

        profiles = ProfileData.getPlayers(game)
        extIds = {extid[0]: extid[1] for extid in GameData.getAllExtid(game)}
        stats = {stat[0]: stat[1] for stat in GameData.getAllGameStats(game)}

        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = {executor.submit(self.process_profile, profile, extIds, stats): profile for profile in profiles}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    data.append(result)

        return {
            'status': 'success',
            'data': data
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
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        version = request.args.get('version')
        userId = request.args.get('userId')

        if not userId:
            return APIConstants.bad_end('No userId!')
        
        if session['id'] != int(userId):
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