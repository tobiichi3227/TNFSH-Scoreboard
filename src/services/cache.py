class CacheService:
    def __init__(self):
        CacheService.inst: "CacheService" = self
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value

    def setnx(self, key, value):
        if key in self.cache:
            return

        self.cache[key] = value
