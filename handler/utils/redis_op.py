from redis import Redis
import json
from data_handler.settings import REDIS


class RedisClient:
    def __init__(self):
        self.client = Redis(
            host=REDIS['HOST'],
            port=REDIS['PORT'],
            db=REDIS.get('DB', 1),
            password=REDIS.get('PASSWORD'),
            decode_responses=True  # خیلی مهم
        )

    # -------------------------
    # Key-Value operations
    # -------------------------
    def set_data(self, key, data, expire=None):
        try:
            self.client.set(key, json.dumps(data), ex=expire)
        except Exception as e:
            raise RuntimeError(f"Redis SET failed: {e}")

    def get_data(self, key):
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except json.JSONDecodeError:
            return None
        except Exception as e:
            raise RuntimeError(f"Redis GET failed: {e}")

    def delete_data(self, key):
        self.client.delete(key)

    # -------------------------
    # Queue operations (List)
    # -------------------------
    def push_queue(self, queue_name, data):
        """Push item to queue (left push)"""
        self.client.lpush(queue_name, json.dumps(data))

    def pop_queue(self, queue_name):
        """Pop item from queue (right pop)"""
        data = self.client.rpop(queue_name)
        return json.loads(data) if data else None

    def get_items(self, queue_name, start=0, end=-1):
        """Get range of items from queue"""
        items = self.client.lrange(queue_name, start, end)
        return [json.loads(item) for item in items]
