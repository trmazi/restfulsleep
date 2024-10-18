from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import distinct
from api.data.mysql import MySQLBase
from api.data.types import Profile, Refid
from api.data.json import JsonEncoded
from typing import Dict, Any, Set, List

class ProfileData:
    @staticmethod
    def getPlayers(game: str) -> List[Dict[str, Any]]:
        with MySQLBase.SessionLocal() as session:
            # Step 1: Retrieve all user IDs for all versions of the specified game
            userIds: Set[int] = set()

            versions = session.query(distinct(Refid.version)).filter(Refid.game == game).all()
            for version in versions:
                version_userIds = session.query(Refid.userId).filter(
                    Refid.game == game,
                    Refid.version == version[0],
                    (Refid.version < 10000) | (Refid.version >= 20000)  # Exclude versions with the bump
                ).all()

                filtered_userIds = (userId for (userId,) in version_userIds)
                userIds.update(filtered_userIds)

        def fetch_latest_profile(userId: int) -> Dict[str, Any]:
            with MySQLBase.SessionLocal() as session:
                refid_query = session.query(Refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    (Refid.version < 10000)  # Exclude versions with the bump
                ).order_by(Refid.version.desc()).first()

                if refid_query:
                    profile = session.query(Profile).filter(Profile.refid == refid_query.refid).first()

                    if profile:
                        rawData = JsonEncoded.deserialize(profile.data)
                        return {
                            'userId': userId,
                            'maxVersion': refid_query.version,
                            'username': rawData.get('username', rawData.get('name', '')),
                            'sgrade': rawData.get('sgrade', None),
                            'dgrade': rawData.get('dgrade', None),
                            'block': rawData.get('block', None),
                            'packet': rawData.get('packet', None),
                            'skill_level': rawData.get('skill_level', None),
                            'jubility': (rawData.get('jubility', 0)) / 10,
                            'profile_skill': (rawData.get('profile_skill', 0)) / 100,
                            'skill': (rawData.get('skill', 0)) / 100,
                        }
            return None

        # Step 2: Get the latest profile information for each user in parallel
        latest_profiles = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_latest_profile, userId) for userId in userIds]
            for future in as_completed(futures):
                profile_info = future.result()
                if profile_info:
                    latest_profiles.append(profile_info)

        return latest_profiles
        
    def getProfile(game: str, version: int, userId: int, noData: bool = False) -> dict:
        with MySQLBase.SessionLocal() as session:

            profile = None
            if version:
                refid_query = session.query(Refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    Refid.version == version
                ).first()

                if refid_query:
                    profile = session.query(Profile).filter(Profile.refid == refid_query.refid).first()
            else:
                refid_query = session.query(Refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    (Refid.version < 10000)
                ).all()

                if refid_query:
                    profile = session.query(Profile).filter(Profile.refid == refid_query[-1].refid).first()

            if profile:
                rawData = JsonEncoded.deserialize(profile.data)
                rawData['machine_judge_adjust'] = None # Block exposing PCBIDs.
                if not noData:
                    return {
                        'userId': userId,
                        'username': rawData.get('username', rawData.get('name', '')),
                        **rawData
                    }
                else:
                    return {
                        'userId': userId,
                        'username': rawData.get('username', rawData.get('name', ''))
                    }
                
            return None
                
    def getVersions(game: str, userId: int) -> dict:
        with MySQLBase.SessionLocal() as session:
            refid_query = session.query(Refid.version).filter(
                Refid.userId == userId,
                Refid.game == game,
                (Refid.version < 10000)
            ).all()

            if refid_query:
                return [refid.version for refid in refid_query]
            
    def updateProfile(game: str, version: int, userId: int, new_profile: dict) -> str | None:
        profile = ProfileData.getProfile(game, version, userId)
        if not profile:
            return 'No profile found!'
        
        if new_profile.get('username') != None:
            new_profile['name'] = new_profile.get('name', new_profile.get('username'))
            
        def update_data(existing_profile, new_data):
            for key, value in new_data.items():
                if isinstance(value, dict):
                    if key == "usergamedata":
                        continue

                    if key not in existing_profile:
                        existing_profile[key] = {}
                    
                    if isinstance(existing_profile[key], dict):
                        update_data(existing_profile[key], value)
                    else:
                        return((None, f"Type mismatch for {key}: expected dict but got {type(value).__name__}"))
                else:
                    if key in existing_profile:
                        if isinstance(existing_profile[key], type(value)):
                            existing_profile[key] = value
                        else:
                            return((None, f"Type mismatch for {key}: expected {type(existing_profile[key]).__name__} but got {type(value).__name__}"))
                    else:
                        existing_profile[key] = value

        with MySQLBase.SessionLocal() as session:
            profile = None
            refid_query = session.query(Refid).filter(
                Refid.userId == userId,
                Refid.game == game,
                Refid.version == version
            ).first()

            if refid_query:
                profile = session.query(Profile).filter(Profile.refid == refid_query.refid).first()

            if profile:
                rawData = JsonEncoded.deserialize(profile.data, True)
                error_code = update_data(rawData, new_profile)
                if error_code:
                    return error_code
            
                profile.data = JsonEncoded.serialize(rawData)
                session.commit()
                
            return None