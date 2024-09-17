from api.data.json import JsonEncoded
from api.data.mysql import MySQLBase
from api.data.types import Machine

from sqlalchemy import text

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
                    'PCBID': machine.pcbid,
                    'name': machine.description,
                    'description': machine.description,
                    'arcadeId': int(machine.arcadeid),
                    'port': str(machine.port),
                    'game': machine.game if machine.game else None,
                    'version': int(machine.version) if machine.version else None,
                    'ota': bool(machine.updaton),
                    'cabinet': False,
                    'data': JsonEncoded.deserialize(machine.data)
                } for machine in machines]
            
    def putMachine(machineId: int = None, arcadeId: int = None, newMachine: dict = None):
        if newMachine is None:
            return None  # No data provided, return None
        
        if arcadeId is None:
            return None
        
        # Check required fields
        if 'name' not in newMachine or newMachine['name'] is None:
            raise ValueError("Machine 'name' is required and cannot be None")
        
        if 'PCBID' not in newMachine or newMachine['PCBID'] is None:
            raise ValueError("Machine 'PCBID' is required and cannot be None")
        
        port = newMachine.get('port')
        
        with MySQLBase.SessionLocal() as session:
            if machineId is not None:
                machine = session.query(Machine).filter(Machine.id == machineId).first()
                if machine is None:
                    return None
            else:
                if newMachine.get('port') is None:
                    while True:
                        port_result = session.execute("SELECT MAX(port) AS port FROM machine").fetchone()
                        port = port_result['port'] + 1 if port_result['port'] is not None else 10000
                        
                        try:
                            machine = Machine(
                                name='なし',
                                description=newMachine.get('name'),
                                pcbid=newMachine.get('PCBID'),
                                arcadeid=arcadeId,
                                port=port,
                                data=JsonEncoded.serialize(newMachine.get('data', {})),
                                updaton=newMachine.get('ota', False)
                            )
                            session.add(machine)
                            session.flush()
                            break
                        except Exception as e:
                            session.rollback()
                            continue
            
            machine.name = 'なし'
            machine.description = newMachine.get('name')
            machine.pcbid = newMachine.get('PCBID')
            machine.arcadeid = arcadeId
            machine.port = port
            machine.updaton = newMachine.get('ota', False)
            machine.data = JsonEncoded.serialize(newMachine.get('data', {}))

            session.commit()

            return {
                'id': int(machine.id),
                'name': machine.description,
                'description': machine.name,
                'PCBID': machine.pcbid,
                'arcadeId': int(machine.arcadeid),
                'port': port,
                'ota': machine.updaton,
                'data': JsonEncoded.deserialize(machine.data)
            }
            
    def fromPCBID(pcbid: str):
        with MySQLBase.SessionLocal() as session:
            machine = session.query(Machine).filter(Machine.pcbid == pcbid).first()
            if machine is None:
                return None
            else:
                return {
                    'id': int(machine.id),
                    'PCBID': machine.pcbid,
                    'name': machine.description,
                    'arcadeId': int(machine.arcadeid),
                    'port': str(machine.port),
                    'game': machine.game if machine.game else None,
                    'version': int(machine.version) if machine.version else None,
                    'ota': bool(machine.updaton),
                    'cabinet': False,
                    'data': JsonEncoded.deserialize(machine.data)
                }