# Minimal Redis cache wrapper (to be implemented when Redis is running)
class Cache:
    def get(self, key: str):
        return None

    def set(self, key: str, value, ttl: int = 600):
        pass


cache_recommendations = Cache()
