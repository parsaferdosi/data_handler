from redis import Redis
import json
from data_handler.settings import REDIS


class RedisClient:
    """
    RedisClient is a lightweight abstraction layer over Redis that centralizes
    connection management, JSON serialization, and commonly used Redis operations.

    This utility is designed to promote reusability, maintainability, and clear
    separation of concerns across the codebase, especially in Django-based or
    asynchronous architectures (ASGI, Celery workers, background tasks).

    Core Responsibilities
    ---------------------
    • Establish and manage a Redis connection using project-level settings
    • Provide simple Key-Value operations with JSON serialization
    • Provide queue-like behavior using Redis Lists (LPUSH / RPOP)
    • Support optional key expiration (TTL)
    • Normalize Redis exceptions into predictable runtime errors

    Configuration
    -------------
    The client relies on a `REDIS` dictionary defined in the project settings:

        REDIS = {
            'HOST': 'localhost',
            'PORT': 6379,
            'DB': 1,                # Optional (default: 1)
            'PASSWORD': None        # Optional
        }

    Usage Example
    -------------
    >>> redis_client = RedisClient()
    >>> redis_client.set_data("user:1", {"name": "Alice"}, expire=60)
    >>> redis_client.get_data("user:1")
    {'name': 'Alice'}

    >>> redis_client.push_queue("events", {"type": "login"})
    >>> redis_client.pop_queue("events")
    {'type': 'login'}

    Design Notes
    ------------
    • All data is stored in Redis as JSON-encoded strings.
    • `decode_responses=True` is enabled, so Redis returns `str` instead of `bytes`.
    • The class is stateless and safe to use across multiple processes,
      including web servers and Celery workers.
    • Thread-safety is delegated to the underlying `redis-py` client.

    Error Handling
    --------------
    • Redis operation failures raise a `RuntimeError` with a descriptive message.
    • Invalid or corrupted JSON payloads safely return `None` instead of crashing.

    Common Use Cases
    ----------------
    • Caching temporary or computed data
    • Implementing lightweight queues
    • Acting as a buffer between API endpoints and background workers
    • Storing short-lived system or processing state
    """
    def __init__(self):
        self.client = Redis(
            host=REDIS['HOST'],
            port=REDIS['PORT'],
            db=REDIS.get('DB', 1),
            password=REDIS.get('PASSWORD'),
            decode_responses=True
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