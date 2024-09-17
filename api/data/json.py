from typing import Optional, Dict, Any
import json

class _BytesEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, bytes):
            # We're abusing lists here, we have a mixed type
            return ['__bytes__'] + [b for b in obj]  # type: ignore
        return json.JSONEncoder.default(self, obj)

class JsonEncoded():
    def deserialize(data: Optional[str]) -> Dict[str, Any]:
        """
        Given a string, deserialize it from JSON.
        """
        if data is None:
            return {}

        def fix(jd: Any) -> Any:
            if type(jd) == dict:
                # Fix each element in the dictionary.
                for key in jd:
                    jd[key] = fix(jd[key])
                return jd

            if type(jd) == list:
                # Could be serialized by us, could be a normal list.
                if len(jd) >= 1 and jd[0] == '__bytes__':
                    # This is a serialized bytestring
                    return None

                # Possibly one of these is a dictionary/list/serialized.
                for i in range(len(jd)):
                    jd[i] = fix(jd[i])
                return jd

            # Normal value, its deserialized version is itself.
            return jd

        return fix(json.loads(data))
    
    def serialize(data: Dict[str, Any]) -> str:
        """
        Given an arbitrary dict, serialize it to JSON.
        """
        return json.dumps(data, cls=_BytesEncoder).encode('utf-8')