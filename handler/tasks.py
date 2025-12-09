from celery import shared_task
from handler.utils.redis_op import RedisClient
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import DataRecord
from django.contrib.auth import get_user_model
import json
User = get_user_model()

class Redis_object:
    __redis = RedisClient().client

    @classmethod
    def get_redis_object(cls):
        if cls.__redis is None:
            cls.__redis = RedisClient().client
        return cls.__redis
@shared_task(queue='notify_queue')
def notify_new_data(data, user_id):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            'type': 'new_data',
            'data': data
        }
    )

@shared_task
def flush_db_queue():
    redis=Redis_object.get_redis_object()
    items=[]
    for _ in range(len(redis.lrange("db_queue", 0, -1))):
        raw = redis.rpop("db_queue")
        if not raw:
            break
        items.append(json.loads(raw))
