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
    
    class Meta:
        fields=["score"]
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
        #create DataBatcher instance and import data from DataCollector instance directly using merge_data method
        DataBatcher_instance=DataBatcher(data_list=DataCollector_instance.merge_data())
        filtered_data=DataFilter(
            data_list=DataBatcher_instance.batch_data(),
            use_dynamic_threshold=True,
        )
        #create SwingAnalyzer instance and import filtered data from DataFilter instance directly using filter method
        SwingAnalyzer_instance=SwingAnalyzer(data_list=filtered_data.filter())
        signals = SwingAnalyzer_instance.analyze()
        if not signals:
            return 0.0

        score = 0
        for sig in signals:
            if sig['signal'] == 'positive':
                score += 1
            else:  # sell
                score -= 1

        score = score / len(signals)
        return round(score, 3)
