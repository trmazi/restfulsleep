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
                    Refid.version == version[0]
                ).all()
                userIds.update(userId for (userId,) in version_userIds)

            # Step 2: Get the latest profile information for each user
            latest_profiles = []
            for userId in userIds:
                refid_query = session.query(Refid).filter(
                    Refid.userId == userId,
                    Refid.game == game
                ).order_by(Refid.version.desc()).first()

                if refid_query:
                    profile = session.query(Profile).filter(Profile.refid == refid_query.refid).first()

                    if profile:
                        rawData = JsonEncoded.deserialize(profile.data)
                        profile_info = {
                            'userId': userId,
                            'maxVersion': refid_query.version,
                            'username': rawData.get('username', rawData.get('name', '')),
                            'sgrade': rawData.get('sgrade', None),
                            'dgrade': rawData.get('dgrade', None),
                            'jubility': (rawData.get('jubility', 0)) / 10,
                            'profile_skill': (rawData.get('profile_skill', 0)) / 100,
                            'skill': (rawData.get('skill', 0)) / 100,
                        }
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
                ).all()

                if refid_query:
                    profile = session.query(Profile).filter(Profile.refid == refid_query[-1].refid).first()

            if profile:
                rawData = JsonEncoded.deserialize(profile.data)
                if not noData:
                    return {
                        'userId': userId,
                        'username': rawData.get('username', rawData.get('name', ''))
                    }
                else:
                    return {
                        'userId': userId,
                        'username': rawData.get('username', rawData.get('name', ''))
                    }
                
            print(userId)
            return {
                'userId': 0,
                'username': ''
            }
                
    def getVersions(game: str, userId: int) -> dict:
        with MySQLBase.SessionLocal() as session:
            refid_query = session.query(Refid.version).filter(
                Refid.userId == userId,
                Refid.game == game,
            ).all()

            if refid_query:
                return [refid.version for refid in refid_query]