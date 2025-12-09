from rest_framework import serializers
from handler.models import DataRecord
from handler.utils.redis_op import RedisClient
from handler.tasks import notify_new_data
import json
class Redis_object:
    __redis = RedisClient()

    @classmethod
    def get_redis_object(cls):
        if cls.__redis is None:
            cls.__redis = RedisClient()
        return cls.__redis

class CreateDataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataRecord
        fields = ['data','date']
    def create(self, validated_data):
        redis=Redis_object.get_redis_object()
        data = {
            'data': validated_data['data'],
            'date': validated_data['date'].isoformat()
        }
        user_id = self.context['request'].user.id
        # Store date in celety redis queues
        notify_new_data.apply_async(args=[data,user_id], queue='notify_queue')
        redis.client.lpush("db_queue", json.dumps({ ... }))
        return data

