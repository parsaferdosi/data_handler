from rest_framework import serializers
from handler.models import DataRecord
from handler.utils.redis_op import RedisClient
import json

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
    bmi=serializers.SerializerMethodField()
    class Meta:
        model = DataRecord
        fields = ['weight', 'height','bmi']
        read_only_fields = ["bmi"]

    def get_bmi(self, obj):
        weight = obj.get('weight')
        height = obj.get('height')
        if height > 0:
            bmi = weight / ((height / 100) ** 2)
            return round(bmi, 2)
        return None
    
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
            'bmi': self.get_bmi(validated_data),
            'user': user.id
        }

        # Save to Redis
        redis = Redis_object.get_redis_object()
        redis.client.rpush("datarecord_queue", json.dumps(data))
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
