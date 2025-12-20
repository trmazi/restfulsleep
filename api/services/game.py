from flask_restful import Resource
import concurrent.futures

from api.constants import APIConstants, ValidatedDict
from api.precheck import RequestPreCheck
from api.data.endpoints.profiles import ProfileData
from api.data.endpoints.game import GameData
from api.data.endpoints.music import MusicData
from api.data.cache import LocalCache

class Game(Resource):
    def process_profile(self, profile, extIds, stats):
        userId = profile.get('userId')
        profile['stats'] = stats.get(userId)
        if profile['stats'] is None:
            return None
        profile['extid'] = extIds.get(userId)
        return profile

    def get(self, game: str):
        sessionState, session = RequestPreCheck.getSession()
        if not sessionState:
            return session
        
        argsState, args = RequestPreCheck.checkArgs({
            'version': str,
            'noUsers': str
        })
        if argsState:
            try:
                version = int(args.get_str('version'))
            except:
                version = None

            try:
                noUsers = (args.get_str('noUsers').lowercase() == 'true')
            except:
                noUsers = False
        
        cacheName = f'juiced_profiles_{game}'

        profileData = None
        if not noUsers:
            if version == None:
                profileData = LocalCache().getCachedData(cacheName)

            if not profileData:
                profileData = []
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    thread_profiles = executor.submit(ProfileData.getAllProfiles, game, version)
                    thread_extids = executor.submit(GameData.getAllExtid, game)
                    thread_stats = executor.submit(GameData.getAllGameStats, game)

                    profiles = thread_profiles.result()
                    extIds = {extid[0]: extid[1] for extid in thread_extids.result()}
                    stats = {stat[0]: stat[1] for stat in thread_stats.result()}

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = {executor.submit(self.process_profile, profile, extIds, stats): profile for profile in profiles}
                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        if result is not None:
                            profileData.append(result)
                if version == None:
                    LocalCache().putCachedData(cacheName, profileData)

        if version: 
            scheduledEventData = GameData.getTimeSensitiveSettings(game, version)
            baseHitChart = MusicData.getHitChart(game, version, 10)
        else:
            scheduledEventData = []
            baseHitChart = []

        return {
            'status': 'success',
            'data': {
                'profiles': profileData,
                'scheduledEvents': scheduledEventData,
                'hitchart': baseHitChart
            }
        }, 200