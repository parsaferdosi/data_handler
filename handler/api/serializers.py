from rest_framework import serializers
from handler.models import DataRecord
from handler.utils.redis_op import RedisClient
from handler.utils.analyzer import SwingAnalyzer, DataCollector, DataBatcher, DataFilter
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
    """
    CreateDataRecordSerializer that handles creation of DataRecord instances
    it imports data into redis queue for celery to process later
    and also notifies via celery notify task in websocket channel
    """
    class Meta:
        model = DataRecord
        fields = ['data','date']
    def create(self, validated_data):
        redis=Redis_object.get_redis_object()
        data = {
            'user_id': self.context['request'].user.id,
            'data': validated_data['data'],
            'date': validated_data['date'].isoformat()
        }
        # Store date in celety redis queues
        notify_new_data.apply_async(args=[data], queue='notify_queue')
        redis.client.lpush("db_queue", json.dumps(data))
        return data

class SwingAnalyzerSerializer(serializers.Serializer):
    """
     SwingAnalyzerSerializer that includes swing trade algorithm 
     this serializer supposed to make a time filter database query and then
     swing analyise the list of data that query gave us as score
    """
    score=serializers.SerializerMethodField()
    start_time=serializers.DateTimeField()
    end_time=serializers.DateTimeField()
    class Meta:
        fields=["score",'start_time','end_time']
    def get_score(self,obj):
        '''
        Docstring for get_score
        
        this method use swing trade algorithm to calculate score
        based on the data provided in obj
        Returns:
            score value as float
        '''
        #create DataCollector instance 
        DataCollector_instance=DataCollector(
            start_time=obj.get('start_time'),
            end_time=obj.get('end_time')
        )
        merge_data=DataCollector_instance.merge_data()
        if not merge_data:
            return "No Data to merge"
        #create DataBatcher instance and import data from DataCollector instance directly using merge_data method
        DataBatcher_instance=DataBatcher(data_list=merge_data)
        data_batch=DataBatcher_instance.batch_data()
        if not data_batch:
            return "No Data to batch"
        filtered_data=DataFilter(
            data_list=data_batch,
            use_dynamic_threshold=True,
        )
        filter=filtered_data.filter()
        if not filter:
            return "No Data after filtering"
        #create SwingAnalyzer instance and import filtered data from DataFilter instance directly using filter method
        SwingAnalyzer_instance=SwingAnalyzer(batched_data=filter)
        signals = SwingAnalyzer_instance.analyze()
        if not signals:
            return "No signals found"
        return signals