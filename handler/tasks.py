from celery import shared_task
from handler.utils.redis_op import RedisClient
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import DataRecord
from django.contrib.auth import get_user_model
from django.db import connections
from django.db.utils import OperationalError
import json
User = get_user_model()

"""
Task definitions for handling asynchronous operations
related to DataRecord insert and notifications.
"""
class Redis_object:
    __redis = RedisClient()

    @classmethod
    def get_redis_object(cls):
        if cls.__redis is None:
            cls.__redis = RedisClient()
        return cls.__redis
@shared_task(queue='notify_queue')
def notify_new_data(data):
    """
    notify_new_data task to send websocket notification about new data record
    
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "root_group",
            {
                "type": "receive",
                "data": data
            }
        )


@shared_task(bind=True)
def flush_db_queue(self):
    """
    flush_db_queue task to process and store DataRecord instances from redis queue to database
    using bulk_create for efficiency.
    """
    
    redis=Redis_object.get_redis_object()
    queue_length = redis.get_length("db_queue")
    if queue_length == 0:
        return   
    records_to_create = []

    # for _ in range(queue_length):
    #     item = redis.pop_queue("db_queue") 
    #     if not item:
    #         break
    #     data = json.loads(item)
    #     try:
    #         user_obj = User.objects.get(id=data["user_id"])
    #     except User.DoesNotExist:
    #         continue
    items=redis.get_items("db_queue",0,queue_length - 1)
    for item in items:
        data=json.loads(item)
        try:
            user_obj=User.objects.get(id=data["user_id"])
        except User.DoesNotExist:
            continue
        record = DataRecord(
            user=user_obj,
            data=data["data"],
            date=data["date"]
        )
        records_to_create.append(record)
    #check database connection before starting bulk insert
    db_connection=connections['default']
    try:
        db_connection.cursor()
    except OperationalError as dbError:
        raise self.retry(exc=dbError,countdown=30)
    
    if records_to_create:
        DataRecord.objects.bulk_create(records_to_create)
    redis.pop_queue("db_queue",items.count)