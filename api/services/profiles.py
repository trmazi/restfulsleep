from flask_restful import Resource
from flask import request

from api.constants import APIConstants
from api.data.endpoints.profiles import ProfileData
from api.data.endpoints.game import GameData

class allPlayers(Resource):
    def get(self, game: str):
        data = []

        profiles = ProfileData.getPlayers(game)
        extIds = {extid[0]: extid[1] for extid in GameData.getAllExtid(game)}
        stats = {stat[0]: stat[1] for stat in GameData.getAllGameStats(game)}

        for profile in profiles:
            userId = profile.get('userId')
            profile['stats'] = stats.get(userId)
            profile['extid'] = extIds.get(userId)
            data.append(profile)

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