from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import distinct, func
from api.data.mysql import MySQLBase
from api.data.types import Profile, Refid
from api.data.json import JsonEncoded
from typing import Dict, Any, Set, List
from api.data.data import BaseData
from api.constants import ValidatedDict

class ProfileData:
    @staticmethod
    def getPlayers(game: str, version: int = None) -> List[Dict[str, Any]]:
        def fetch_profile_for_version(userId: int, version: int) -> Dict[str, Any]:
            with MySQLBase.SessionLocal() as session:
                refid_query = session.query(Refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    Refid.version == version
                ).first()

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

        with MySQLBase.SessionLocal() as session:
            userIds: Set[int] = set()

            if version is not None:
                # Only get user IDs for the specific version
                version_userIds = session.query(Refid.userId).filter(
                    Refid.game == game,
                    Refid.version == version
                ).all()
                userIds.update(userId for (userId,) in version_userIds)
            else:
                # Get all user IDs for all valid versions (excluding bumps)
                versions = session.query(distinct(Refid.version)).filter(Refid.game == game).all()
                for version_row in versions:
                    v = version_row[0]
                    if v >= 10000 and v < 20000:
                        continue  # skip bump versions
                    version_userIds = session.query(Refid.userId).filter(
                        Refid.game == game,
                        Refid.version == v
                    ).all()
                    userIds.update(userId for (userId,) in version_userIds)

        # Step 2: Get profile information in parallel
        profiles = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            if version is not None:
                futures = [executor.submit(fetch_profile_for_version, userId, version) for userId in userIds]
            else:
                futures = [executor.submit(fetch_latest_profile, userId) for userId in userIds]

            for future in as_completed(futures):
                profile_info = future.result()
                if profile_info:
                    profiles.append(profile_info)

        return profiles
        
    def getProfile(game: str, version: int, userId: int, noData: bool = False) -> dict:
        with MySQLBase.SessionLocal() as session:
            profile = None
            if version:
                # Combine Refid and Profile queries into a single JOIN query
                profile = session.query(Profile).join(Refid, Refid.refid == Profile.refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    Refid.version == version
                ).first()
            else:
                # Fetch the latest Refid and Profile in one query, ordering by version descending
                profile = session.query(Profile).join(Refid, Refid.refid == Profile.refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    Refid.version < 10000
                ).order_by(Refid.version.desc()).first()

            if profile:
                rawData = JsonEncoded.deserialize(profile.data)
                rawData['machine_judge_adjust'] = None  # Block exposing PCBIDs
                return {
                    'userId': userId,
                    'username': rawData.get('username', rawData.get('name', '')),
                    **(rawData if not noData else {})
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

    def getProfileName(game: str, version: int, userId: int) -> str | None:
        with MySQLBase.SessionLocal() as session:
            if version:
                refid = session.query(Refid.refid).filter_by(
                    userId=userId,
                    game=game,
                    version=version
                ).scalar()
            else:
                refid = session.query(Refid.refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    Refid.version < 10000
                ).order_by(Refid.version.desc()).limit(1).scalar()

            if refid:
                data = session.query(Profile.data).filter_by(refid=refid).scalar()
                if data:
                    deserialized = JsonEncoded.deserialize(data)
                    return deserialized.get("username") or deserialized.get("name")
            return None
            
    def updateProfile(game: str, version: int, userId: int, new_profile: dict) -> str | None:
        profile = ProfileData.getProfile(game, version, userId)
        if not profile:
            return 'No profile found!'
        
        if new_profile.get('username') != None:
            new_profile['name'] = new_profile.get('name', new_profile.get('username'))

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
                error_code = BaseData.update_data(rawData, new_profile)
                if error_code:
                    return error_code
            
                profile.data = JsonEncoded.serialize(rawData)
                session.commit()
                
            return None