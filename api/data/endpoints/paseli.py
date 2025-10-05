from api.constants import ValidatedDict
from api.data.time import Time
from api.data.json import JsonEncoded
from api.data.mysql import MySQLBase
from api.data.types import Audit, Balance

class PaseliData:   
    def getArcadeBalances(arcadeId: int) -> list[ValidatedDict]:
        with MySQLBase.SessionLocal() as session:
            balances = session.query(Balance).filter(Balance.arcadeid == arcadeId).all()
            if balances is None:
                return None
            else:
                return [ValidatedDict({
                    'userId': int(balance.userid),
                    'balance': int(balance.balance)
                }) for balance in balances]
            
    def putArcadeBalance(arcadeId: int, userId: int, credit: int) -> bool:
        with MySQLBase.SessionLocal() as session:
            try:
                balance = session.query(Balance).filter(Balance.arcadeid == arcadeId, Balance.userid == userId).first()
                if balance is None:
                    balance = Balance()
                    balance.arcadeid = arcadeId
                    balance.userid = userId
                    balance.balance = 0
                    session.add(balance)
                
                balance.balance += credit
                session.commit()
                return True
            except Exception as e:
                    session.rollback()
                    return False
            
    def getTransactions(arcadeId: int) -> list[ValidatedDict]:
        with MySQLBase.SessionLocal() as session:
            transactions = session.query(Audit).filter(Audit.arcadeid == arcadeId, Audit.type == "paseli_transaction").all()
            if transactions is None:
                return None
            else:
                return [ValidatedDict({
                    'id': int(transaction.id),
                    'timestamp': int(transaction.timestamp),
                    'data': JsonEncoded.deserialize(transaction.data)
                }) for transaction in transactions]
            
    def putTransaction(arcadeId: int, userId: int, credit: int) -> bool:
        with MySQLBase.SessionLocal() as session:
            try:
                transaction = Audit()
                transaction.arcadeid = arcadeId
                transaction.userid = userId
                transaction.type = "paseli_transaction"
                transaction.timestamp = Time.now()
                transaction.data = JsonEncoded.serialize({
                    'delta': credit,
                    'service': 0,
                    'reason': 'WebUI Adjustment',
                })
                session.add(transaction)
                session.commit()
                return True
            
            except Exception as e:
                    session.rollback()
                    return False