class BaseData():
    BAD_KEYS = ["usergamedata", "beta", "userId", "stats", "is_beta", "admin", "beta", "hitChart"]
    @classmethod
    def update_data(cls, existing_data, new_data):
        for key, value in new_data.items():
            if key in BaseData.BAD_KEYS:
                continue

            if value is None:
                # If the value is None, remove the key from existing_data
                if key in existing_data:
                    del existing_data[key]
            elif isinstance(value, dict):
                if key in BaseData.BAD_KEYS:
                    continue
                
                if key not in existing_data:
                    existing_data[key] = {}
                
                if isinstance(existing_data[key], dict):
                    cls.update_data(existing_data[key], value)
                else:
                    return (None, f"Type mismatch for {key}: expected dict but got {type(existing_data[key]).__name__}")
            else:
                if key in existing_data:
                    if isinstance(existing_data[key], type(value)):
                        existing_data[key] = value
                    else:
                        return (None, f"Type mismatch for {key}: expected {type(existing_data[key]).__name__} but got {type(value).__name__}")
                else:
                    existing_data[key] = value