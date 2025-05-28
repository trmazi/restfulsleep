import argparse
import yaml
import concurrent.futures
from api.constants import GameConstants, VersionConstants
from api.data.mysql import MySQLBase
from api.data.cache import LocalCache
from api.data.endpoints.profiles import ProfileData
from api.data.endpoints.game import GameData
from api.data.endpoints.music import MusicData
from api.data.endpoints.score import ScoreData

class Scheduler:
    @staticmethod
    def process_profile(profile, extIds, stats):
        userId = profile.get('userId')
        profile['stats'] = stats.get(userId)
        if profile['stats'] is None:
            return None
        profile['extid'] = extIds.get(userId)
        return profile

    def run_scheduled_work(self, config: dict):
        db_config = config.get('database', {})
        if db_config:
            MySQLBase.updateConfig(db_config)

        cacheConfig = config.get('cache', {})
        if cacheConfig:
            LocalCache.updateConfig(cacheConfig)

        gameList = [
            GameConstants.BEATSTREAM,
            GameConstants.DANCE_RUSH,
            GameConstants.DDR,
            GameConstants.DDRCLASS,
            GameConstants.DDROMNI,
            GameConstants.DRUMMANIA,
            GameConstants.FUTURETOMTOM,
            GameConstants.GITADORA_DM,
            GameConstants.GITADORA_GF,
            GameConstants.GUITARFREAKS,
            GameConstants.IIDX,
            GameConstants.IIDXCLASS,
            GameConstants.JUBEAT,
            GameConstants.MUSECA,
            GameConstants.NOSTALGIA,
            GameConstants.POPN_MUSIC,
            GameConstants.REFLEC_BEAT,
            GameConstants.SDVX,
            GameConstants.TSUMTSUM,
        ]

        cacheList = [
            {
                'game': GameConstants.DDR,
                'versions': [VersionConstants.DDR_ACE, VersionConstants.DDR_A20, VersionConstants.DDR_A20_PLUS, VersionConstants.DDR_A3]
            },
            {
                'game': GameConstants.DDROMNI,
                'versions': [VersionConstants.DDR_OMNI_MIX]
            },
            {
                'game': GameConstants.DRUMMANIA,
                'versions': [VersionConstants.DRUMMANIA_V8, VersionConstants.DRUMMANIA_V7]
            },
            {
                'game': GameConstants.GITADORA_DM,
                'versions': [VersionConstants.GITADORA_HIGH_VOLTAGE, VersionConstants.GITADORA_FUZZUP]
            },
            {
                'game': GameConstants.GITADORA_GF,
                'versions': [VersionConstants.GITADORA_HIGH_VOLTAGE, VersionConstants.GITADORA_FUZZUP]
            },
            {
                'game': GameConstants.GUITARFREAKS,
                'versions': [VersionConstants.GUITARFREAKS_V8, VersionConstants.GUITARFREAKS_V7]
            },
            {
                'game': GameConstants.IIDX,
                'versions': [VersionConstants.IIDX_CASTHOUR, VersionConstants.IIDX_RESIDENT, VersionConstants.IIDX_EPOLIS]
            },
            {
                'game': GameConstants.JUBEAT,
                'versions': [VersionConstants.JUBEAT_CLAN, VersionConstants.JUBEAT_FESTO, VersionConstants.JUBEAT_AVE]
            },
            {
                'game': GameConstants.POPN_MUSIC,
                'versions': [VersionConstants.POPN_MUSIC_KAIMEI_RIDDLES, VersionConstants.POPN_MUSIC_UNILAB]
            },
            {
                'game': GameConstants.SDVX,
                'versions': [VersionConstants.SDVX_VIVID_WAVE, VersionConstants.SDVX_EXCEED_GEAR]
            },
        ]

        for game in gameList:
            cacheName = f'juiced_profiles_{game}'
            print(f'[RestfulCache] Checking {cacheName}')
            profileData = LocalCache().getCachedData(cacheName)

            if not profileData:
                profileData = []
                profiles = ProfileData.getPlayers(game)
                extIds = {extid[0]: extid[1] for extid in GameData.getAllExtid(game)}
                stats = {stat[0]: stat[1] for stat in GameData.getAllGameStats(game)}

                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    futures = {executor.submit(Scheduler.process_profile, profile, extIds, stats): profile for profile in profiles}
                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        if result is not None:
                            profileData.append(result)
                LocalCache().putCachedData(cacheName, profileData)
                print(f'[RestfulCache] Cached {len(profileData)} profiles for {game}')

            # Make a cache of music data for this game
            musicData = MusicData.getAllMusic(game)
            MusicData.getAllSongs(game)
            print(f'[RestfulCache] Cached {len(musicData)} musicIds for {game}')

        for cacheEntry in cacheList:
            for version in cacheEntry.get('versions'):
                print(f'[RestfulCache] Caching {cacheEntry.get("game")} records for {version}')
                cacheData = ScoreData.getAllRecords(cacheEntry.get('game'), version)
                print(f'[RestfulCache] Cached {len(cacheData)} entries for {cacheEntry.get("game")}, {version}')

parser = argparse.ArgumentParser(description="A scheduler for work that needs to be done periodically.")
parser.add_argument("-c", "--config", help="Core configuration. Defaults to config.yaml", type=str, default="config.yaml")
args = parser.parse_args()

# Set up global configuration
config = yaml.safe_load(open(args.config))

# Run out of band work
Scheduler().run_scheduled_work(config)
