class BaseData():
    @classmethod
    def update_data(self, existing_data, new_data):
        for key, value in new_data.items():
            if isinstance(value, dict):
                if key == "usergamedata":
                    continue

                if key not in existing_data:
                    existing_data[key] = {}
                
                if isinstance(existing_data[key], dict):
                    BaseData.update_data(existing_data[key], value)
                else:
                    return((None, f"Type mismatch for {key}: expected dict but got {type(value).__name__}"))
            else:
                if key in existing_data:
                    if isinstance(existing_data[key], type(value)):
                        existing_data[key] = value
                    else:
                        return((None, f"Type mismatch for {key}: expected {type(existing_data[key]).__name__} but got {type(value).__name__}"))
                else:
                    existing_data[key] = value