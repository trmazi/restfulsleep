class APIConstants:
    def bad_end(error: str) -> dict:
        return {'status': 'error', 'error_code': error}