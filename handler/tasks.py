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
    records_to_create = []

    for key in keys:
        key = key.decode("utf-8")

        if key == "data_record_key":
            continue

        if not key.isdigit():
            continue

        data = redis.get_data(key)
        if not data:
            continue

        try:
            user_obj = User.objects.get(id=data["user"])
        except User.DoesNotExist:
            continue
        record = DataRecord(
            user=user_obj,
            weight=data["weight"],
            height=data["height"],
            bmi = data["bmi"]

        )
        records_to_create.append(record)
        # بعد از مصرف، پاکش کن
        redis.delete_data(key)
    try:
        DataRecord.objects.bulk_create(records_to_create)
    except Exception as e:
        # log خطا یا ignore
        print(f"Error during bulk_create: {e}")