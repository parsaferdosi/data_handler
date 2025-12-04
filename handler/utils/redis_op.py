from redis import Redis
import json
from data_handler.settings import REDIS

class RedisClient:
    def __init__(self):
        self.client = Redis(
            host=REDIS['HOST'],
            port=REDIS['PORT'],
            db=REDIS.get('DB', 1),
            password=REDIS.get('PASSWORD', None)
        )

    def set_data(self, key, data, expire=None):
        data_json = json.dumps(data)
        self.client.set(name=key, value=data_json, ex=expire)

    def get_data(self, key):
        data_json = self.client.get(name=key)
        if data_json:
            return json.loads(data_json)
        return None

    def delete_data(self, key):
        self.client.delete(key)

    def generate_key(self):
        return self.client.incr("data_record_key")
