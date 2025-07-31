from typing import Optional, Dict, Any
import json

class _BytesEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, bytes):
            # We're abusing lists here, we have a mixed type
            return ['__bytes__'] + [b for b in obj]  # type: ignore
        return json.JSONEncoder.default(self, obj)

class JsonEncoded:
    @staticmethod
    def deserialize(data: Optional[str], include_bytes: bool = False) -> Dict[str, Any]:
        if data is None:
            return {}

        deserialized_data = json.loads(data)

        if not include_bytes:
            return deserialized_data

        def fix(jd: Any) -> Any:
            if isinstance(jd, list):
                if len(jd) >= 1 and jd[0] == '__bytes__':
                    if include_bytes:
                        try:
                            return bytes(bytearray(jd[1:]))
                        except TypeError:
                            print(f"Malformed byte: {jd}")
                    else:
                        return jd

                return [fix(item) for item in jd]

            elif isinstance(jd, dict):
                return {key: fix(value) for key, value in jd.items()}

            return jd

        return fix(deserialized_data) 
    
    def serialize(data: Dict[str, Any]) -> str:
        """
        Given an arbitrary dict, serialize it to JSON.
        """
        return json.dumps(data, cls=_BytesEncoder).encode('utf-8')