from .models import DataRecord
from django.contrib.auth.models import User
from handler.utils.redis_op import RedisClient
from celery import shared_task

class Redis_object:
    __redis = RedisClient()

    @classmethod
    def get_redis_object(cls):
        if cls.__redis is None:
            cls.__redis = RedisClient()
        return cls.__redis


@shared_task
def scan_redis():
    redis = Redis_object.get_redis_object()
    client = redis.client

    keys = client.keys("*")

    for key in keys:
        key = key.decode("utf-8")

        if key == "data_record_key":
            continue

        if not key.isdigit():
            continue

        data = redis.get_data(key)
        if not data:
            continue


        user_obj = User.objects.get(id=data["user"])

        DataRecord.objects.create(
            user=user_obj,
            weight=data["weight"],
            height=data["height"],
        )

        # بعد از مصرف، پاکش کن
        redis.delete_data(key)
