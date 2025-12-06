from .models import DataRecord
from django.contrib.auth.models import User
from handler.utils.redis_op import RedisClient
from celery import shared_task
import json
class Redis_object:
    __redis = RedisClient()

    @classmethod
    def get_redis_object(cls):
        if cls.__redis is None:
            cls.__redis = RedisClient()
        return cls.__redis
    
@shared_task
def scan_redis_queue():
    redis = Redis_object.get_redis_object()
    
    queue_length = redis.client.llen("datarecord_queue")
    if queue_length == 0:
        return 

    records_to_create = []

    for _ in range(queue_length):
        item = redis.client.lpop("datarecord_queue") 
        if not item:
            break
        data = json.loads(item)
        try:
            user_obj = User.objects.get(id=data["user"])
        except User.DoesNotExist:
            continue

        record = DataRecord(
            user=user_obj,
            weight=data["weight"],
            height=data["height"],
            bmi=data["bmi"]
        )
        records_to_create.append(record)

    if records_to_create:
        DataRecord.objects.bulk_create(records_to_create)
