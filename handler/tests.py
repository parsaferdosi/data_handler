from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
import random

from handler.models import DataRecord
from handler.utils.redis_op import RedisClient
from handler.tasks import scan_redis_queue

User = get_user_model()
class Redis_object:
    __redis = RedisClient()

    @classmethod
    def get_redis_object(cls):
        if cls.__redis is None:
            cls.__redis = RedisClient()
        return cls.__redis

def generate_weight():
    return random.randint(1, 150)

def generate_height():
    return random.randint(30, 250)

class HighLoadTransactionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="test", password="password123")

    def setUp(self):
        self.client = APIClient()
        self.client.login(username="test", password="password123")
        self.redis = Redis_object.get_redis_object()

    def test_transactions(self):
        url = reverse("datarecord-upload")
        requests_amount = 1000

        payloads = []

        # مرحله 1: POST داده‌ها به API
        for i in range(requests_amount):
            payload = {
                "weight": generate_weight(),
                "height": generate_height(),
            }
            payloads.append(payload)
            response = self.client.post(url, data=payload, format="json")
            self.assertIn(response.status_code, [200, 201, 202])
        queue_length = self.redis.client.llen("datarecord_queue")
        self.assertEqual(queue_length, requests_amount)

        # بررسی اینکه داده‌ها در Redis اضافه شدند

        # مرحله 2: اجرای ورکر سلری (سینک)
        scan_redis_queue.apply()  
        # # مستقیم تابع را اجرا می‌کنیم

        # بررسی دیتابیس
        for payload in payloads:
            exists = DataRecord.objects.filter(
                user=self.user,
                weight=payload['weight'],
                height=payload['height'],
            ).exists()
            self.assertTrue(exists)

        # بررسی اینکه Redis خالی شده
        redis_keys_after = self.redis.client.keys("*")
        self.assertFalse(any(k.decode("utf-8").isdigit() for k in redis_keys_after))
