from api.data.mysql import MySQLBase
from api.data.types import Achievement, Refid
from api.data.json import JsonEncoded

class AchievementData:
    @staticmethod        
    def getAchievement(game: str, version: int, userId: int, achievementType: str, achievementId: int) -> dict:
        '''
        Given the game, version, userId, achievementType, achievementId and returns the achievement data.
        '''
        with MySQLBase.SessionLocal() as session:
            achievement = None
            if version:
                refid_query = session.query(Refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    Refid.version == version
                ).first()

                if refid_query:
                    achievement = session.query(Achievement).filter(Achievement.refid == refid_query.refid, Achievement.id == achievementId, Achievement.type == achievementType).first()
            else:
                refid_query = session.query(Refid).filter(
                    Refid.userId == userId,
                    Refid.game == game,
                    (Refid.version < 10000)
                ).all()

                if refid_query:
                    achievement = session.query(Achievement).filter(Achievement.refid == refid_query[-1].refid, Achievement.id == achievementId, Achievement.type == achievementType).first()

            if achievement:
                rawData = JsonEncoded.deserialize(achievement.data)
                return rawData
                
            return None