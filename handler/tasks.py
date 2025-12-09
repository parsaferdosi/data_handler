from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import DataRecord
from django.contrib.auth import get_user_model
User = get_user_model()

@shared_task(queue='notify_queue')
def notify_new_data(data, user_id):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            'type': 'new_data',
            'data': data
        }
    )

    save_data_task.apply_async(args=[data, user_id], queue='db_queue')


@shared_task(queue='db_queue')
def save_data_task(data, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    DataRecord.objects.create(
        user=user,
        weight=data['weight'],
        height=data['height'],
        bmi=data['bmi']
    )
