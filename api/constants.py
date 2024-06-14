class APIConstants:
    def bad_end(error: str) -> dict:
        return {'status': 'error', 'error_code': error}
    
    def soft_end(error: str) -> dict:
        return {'status': 'warn', 'error_code': error}