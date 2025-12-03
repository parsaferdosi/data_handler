from rest_framework import serializers
from handler.models import DataRecord
from handler.utils.redis_op import RedisClient
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class Redis_object:
    __redis = RedisClient()

    @classmethod
    def get_redis_object(cls):
        if cls.__redis is None:
            cls.__redis = RedisClient()
        return cls.__redis


class ListDataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataRecord
        fields = ['id', 'user', 'bmi']
        read_only_fields = ['id', 'user', 'bmi']


class CreateDataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataRecord
        fields = ['weight', 'height']

    def validate(self, attrs):
        weight = attrs.get('weight')
        height = attrs.get('height')
        if weight <= 0:
            raise serializers.ValidationError("Weight must be a positive number.")
        if height <= 0:
            raise serializers.ValidationError("Height must be a positive number.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user

        data = {
            'weight': validated_data['weight'],
            'height': validated_data['height'],
            'user': user.id
        }

        # Save to Redis
        redis = Redis_object.get_redis_object()
        key = redis.generate_key()
        redis.set_data(key, data, expire=None)

        # Send WebSocket Message ✓ (fixed)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "root_group",
            {
                "type": "receive",
                "data": data
            }
        )

        return data


class DetailDataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataRecord
        fields = ['id', 'user', 'weight', 'height', 'bmi', 'timestamp']
        read_only_fields = ['id', 'user', 'bmi', 'timestamp']

    def update(self, instance, validated_data):
        instance.weight = validated_data.get('weight', instance.weight)
        instance.height = validated_data.get('height', instance.height)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()
