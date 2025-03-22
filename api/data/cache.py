import os
import pickle
import time
from typing import Any
from api.constants import ValidatedDict

class LocalCache:
    CACHE_PATH = None
    CACHE_EXPIRATION = 300000 # 5 minutes

    @staticmethod
    def updateConfig(cacheConfig: dict) -> None:
        cacheConfig = ValidatedDict(cacheConfig)
        LocalCache.CACHE_PATH = cacheConfig.get_str('cache_path', None)
        LocalCache.CACHE_EXPIRATION = cacheConfig.get_int('expiration', 300000)

    def getCachedData(self, fileName: str) -> Any | None:
        '''
        Check for a cached file, return it if not expired.
        If the file has expired, send None. The caller is expected to fetch fresh data.
        '''
        fullPath = os.path.join(self.CACHE_PATH, fileName) + '.pkl'
        if os.path.exists(fullPath):
            file_age = time.time() - os.path.getmtime(fullPath)
            if file_age < self.CACHE_EXPIRATION:
                with open(fullPath, 'rb') as inFile:
                    _, cached_data = pickle.load(inFile)
                return cached_data
        return None
    
    def putCachedData(self, fileName: str, data: Any) -> bool:
        '''
        Given a dataset, pickle it, save it.
        '''
        fullPath = os.path.join(self.CACHE_PATH, fileName) + '.pkl'
        try:
            with open(fullPath, 'wb') as outFile:
                pickle.dump((time.time(), data), outFile)
            return True
        except: 
            return False