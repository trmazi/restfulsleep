from api.data.json import JsonEncoded
from api.data.mysql import MySQLBase
from api.data.types import Machine

class MachineData:   
    def getArcadeMachines(arcadeId: int):
        with MySQLBase.SessionLocal() as session:
            machines = session.query(Machine).filter(Machine.arcadeid == arcadeId).all()
            if machines is None:
                return None
            else:
                return [{
                    'id': int(machine.id),
                    'pcbId': machine.pcbid,
                    'name': machine.name,
                    'description': machine.description,
                    'arcadeId': int(machine.arcadeid),
                    'port': str(machine.port),
                    'game': machine.game if machine.game else None,
                    'version': int(machine.version) if machine.version else None,
                    'ota': bool(machine.updaton),
                    'data': JsonEncoded.deserialize(machine.data)
                } for machine in machines]