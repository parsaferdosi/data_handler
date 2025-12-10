from ..models import DataRecord
from django.utils import timezone
from .redis_op import RedisClient
import json
import statistics

"""
Utility classes and functions for data analysis, including data collection,
batching, filtering, and swing trade analysis.
classes are independent and can be used separately.
"""
class redis_object:
    __redis = RedisClient()

    @classmethod
    def get_redis_object(cls):
        if cls.__redis is None:
            cls.__redis = RedisClient()
        return cls.__redis

class DataCollector:
    """
    A class to collect data records from the database and redis within a specified time range.
    and merge them into a single list.
    """
    QUEUE_NAME = "db_queue"
    def __init__(self,start_time=None,end_time=None):
        self.redis = redis_object.get_redis_object().client
        self.start_time=start_time
        self.end_time=end_time or timezone.now()
    def collect_data_from_db(self):
        """
        Collect data records from the database within the specified time range.
        """
        
        queryset=DataRecord.objects.filter(
            date__gte=self.start_time,
            date__lte=self.end_time
        ).values(
        'data','date'
        )
        return list(queryset)
    def collect_data_from_redis(self):
        """
        Collect data records from Redis queue within the specified time range.
        """
        try:
            raw_data_list = self.redis.lrange(self.QUEUE_NAME, 0, -1)
        except Exception:
            raw_data_list = []
        data_list = []
        for raw_data in raw_data_list:
                data_dict = json.loads(raw_data)
                data_date = timezone.datetime.fromisoformat(data_dict['date'])
                if self.start_time <= data_date <= self.end_time:
                    data_list.append({
                        'data': data_dict['data'],
                        'date': data_date
                    })
        return data_list
    def merge_data(self):
        """
        Merge data records from the database and Redis into a single list.
        """
        db_data = self.collect_data_from_db()
        redis_data = self.collect_data_from_redis()
        merged_data = db_data + redis_data
        merged_data.sort(key=lambda x: x['date'])
        return merged_data
class DataBatcher:
    """
    a class to batch data into smaller chunks
    of 5 mins intervals
    and then returns a list of dicts with 3 elements each
    start_time in that batch
    average data in that batch
    variance of data in that batch
    """
    def __init__(self,data_list,batch_interval_minutes=5):
        self.data_list=data_list
        self.batch_interval_minutes=batch_interval_minutes
    def batch_data(self):
        """
        Docstring for batch_data
        Batches the data into intervals and calculates average and variance for each batch.
        Returns:
            list of dicts with 'start_time', 'average', and 'variance' for each batch.
        """
        if not self.data_list:
            return []
        batched_data = []
        batch_start_time = self.data_list[0]['date']
        batch_end_time = batch_start_time + timezone.timedelta(minutes=self.batch_interval_minutes)
        current_batch = []
        for record in self.data_list:
            record_time = record['date']
            if record_time < batch_end_time:
                current_batch.append(record['data'])
            else:
                if current_batch:
                    average = sum(current_batch) / len(current_batch)
                    variance = sum((x - average) ** 2 for x in current_batch) / len(current_batch)
                    batched_data.append({
                        'start_time': batch_start_time,
                        'average': average,
                        'variance': variance
                    })
                batch_start_time = record_time
                batch_end_time = batch_start_time + timezone.timedelta(minutes=self.batch_interval_minutes)
                current_batch = [record['data']]
        if current_batch:
            average = sum(current_batch) / len(current_batch)
            variance = sum((x - average) ** 2 for x in current_batch) / len(current_batch)
            batched_data.append({
                'start_time': batch_start_time,
                'average': average,
                'variance': variance
            })
        return batched_data
class DataFilter:
    """
    Advanced data filtering based on statistical volatility analysis.
    """

    def __init__(
        self,
        data_list,
        variance_threshold=None,
        use_dynamic_threshold=False,
        zscore_threshold=None,
        soft_mode=True
    ):
        self.data_list = data_list
        self.variance_threshold = variance_threshold
        self.use_dynamic_threshold = use_dynamic_threshold
        self.zscore_threshold = zscore_threshold
        self.soft_mode = soft_mode

    def dynamic_threshold(self):
        """
        Docstring for dynamic_threshold
        calculate dynamic threshold based on mean and standard deviation of variances
        """
        valid_variances = [
            d['variance']
            for d in self.data_list
            if isinstance(d.get('variance'), (int, float))
        ]
        if not valid_variances:
            return 0
        mean = statistics.mean(valid_variances)
        std = statistics.stdev(valid_variances) if len(valid_variances) > 1 else 0
        return mean + std

    def filter(self):
        """
        Docstring for filter
        Filters data records based on variance thresholds and z-scores.
        Returns:
            list of filtered data records.
            
        """
        if not self.data_list:
            return []

        threshold = (
            self.dynamic_threshold()
            if self.use_dynamic_threshold
            else self.variance_threshold
        )

        variances = [d['variance'] for d in self.data_list if 'variance' in d]
        mean = statistics.mean(variances) if variances else 0
        std = statistics.stdev(variances) if len(variances) > 1 else 0

        filtered = []

        for record in self.data_list:
            variance = record.get('variance')
            if variance is None or not isinstance(variance, (int, float)):
                continue

            # Z-score mode
            if self.zscore_threshold is not None and std != 0:
                z = (variance - mean) / std
                if z >= self.zscore_threshold:
                    record['zscore'] = z
                    filtered.append(record)
                elif self.soft_mode and z > 0:
                    record['zscore'] = z
                    filtered.append(record)

            # Threshold mode
            elif threshold is not None:
                if variance >= threshold:
                    filtered.append(record)
                elif self.soft_mode and variance >= (threshold * 0.5):
                    record['soft_flag'] = True
                    filtered.append(record)

        return filtered
class SwingAnalyzer:
    """
    Docstring for SwingAnalyzer
    Implements a swing trade analysis algorithm.
    
    """
    def __init__(self,batched_data):
        self.batched_data=batched_data
    def analyze(self):
        """
        Docstring for analyze
        Analyzes batched data to identify swing trade opportunities.
        Returns:
            list of swing trade signals.
        """
        signals = []
        for i in range(1, len(self.batched_data) - 1):
            prev_avg = self.batched_data[i - 1]['average']
            curr_avg = self.batched_data[i]['average']
            next_avg = self.batched_data[i + 1]['average']

            if curr_avg > prev_avg and curr_avg > next_avg:
                signals.append({
                    'time': self.batched_data[i]['start_time'],
                    'signal': 'possitive',
                    'average': curr_avg
                })
            elif curr_avg < prev_avg and curr_avg < next_avg:
                signals.append({
                    'time': self.batched_data[i]['start_time'],
                    'signal': 'negetive',
                    'average': curr_avg
                })
        return signals