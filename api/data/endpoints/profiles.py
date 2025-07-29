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
    def getAllProfiles(game: str, version: int = None) -> List[Dict[str, Any]]:
        profiles = []
        with MySQLBase.SessionLocal() as session:
            if version is not None:
                query_results = (
                    session.query(
                        Refid.userId,
                        Refid.version,
                        Profile.data
                    )
                    .join(Profile, Refid.refid == Profile.refid)
                    .filter(
                        Refid.game == game,
                        Refid.version == version
                    )
                    .all()
                )

            else:
                latest_version_subquery = (
                    session.query(
                        Refid.userId,
                        func.max(Refid.version).label("max_version")
                    )
                    .filter(
                        Refid.game == game,
                        Refid.version < 10000
                    )
                    .group_by(Refid.userId)
                    .subquery("latest_refid")
                )

                query_results = (
                    session.query(
                        Refid.userId,
                        Refid.version,
                        Profile.data
                    )
                    .join(
                        latest_version_subquery,
                        (Refid.userId == latest_version_subquery.c.userId) &
                        (Refid.version == latest_version_subquery.c.max_version)
                    )
                    .join(Profile, Refid.refid == Profile.refid)
                    .filter(Refid.game == game)
                    .all()
                )

            for userId, maxVersion, profile_data in query_results:
                rawData = JsonEncoded.deserialize(profile_data)
                profiles.append({
                    'userId': userId,
                    'maxVersion': maxVersion,
                    'username': rawData.get('username', rawData.get('name', '')),
                    'sgrade': rawData.get('sgrade', None),
                    'dgrade': rawData.get('dgrade', None),
                    'block': rawData.get('block', None),
                    'packet': rawData.get('packet', None),
                    'skill_level': rawData.get('skill_level', None),
                    'jubility': (rawData.get('jubility', 0)) / 10,
                    'profile_skill': (rawData.get('profile_skill', 0)) / 100,
                    'skill': (rawData.get('skill', 0)) / 100,
                })

        return profiles
        
    def getProfile(game: str, version: int, userId: int, noData: bool = False) -> dict:
        with MySQLBase.SessionLocal() as session:
            profile = None
            if version:
                profile = session.query(Profile).join(Refid, Refid.refid == Profile.refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    Refid.version == version
                ).first()
            else:
                profile = session.query(Profile).join(Refid, Refid.refid == Profile.refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    Refid.version < 10000
                ).order_by(Refid.version.desc()).first()

            if profile:
                rawData = JsonEncoded.deserialize(profile.data)
                rawData['machine_judge_adjust'] = None
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