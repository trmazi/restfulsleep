from api.constants import ValidatedDict
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