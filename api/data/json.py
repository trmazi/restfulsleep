from typing import Optional, Dict, Any
import ujson

class JsonEncoded:
    @staticmethod
    def deserialize(data: Optional[str], include_bytes: bool = False) -> Dict[str, Any]:
        if data is None:
            return {}

        deserialized_data = ujson.loads(data)

        if not include_bytes:
            return deserialized_data

        def fix(jd: Any) -> Any:
            if isinstance(jd, list):
                if len(jd) >= 1 and jd[0] == '__bytes__':
                    try:
                        return bytes(bytearray(jd[1:]))
                    except TypeError:
                        print(f"Malformed byte: {jd}")
                        return jd
                return [fix(item) for item in jd]
            elif isinstance(jd, dict):
                return {key: fix(value) for key, value in jd.items()}
            return jd

        return fix(deserialized_data)

    @staticmethod
    def serialize(data: Dict[str, Any]) -> str:
        """
        Given an arbitrary dict, serialize it to JSON using ujson.
        """

        def preprocess(obj: Any) -> Any:
            if isinstance(obj, bytes):
                return ['__bytes__'] + list(obj)
            elif isinstance(obj, dict):
                return {k: preprocess(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [preprocess(item) for item in obj]
            return obj

        serialized_data = preprocess(data)
        return ujson.dumps(serialized_data)