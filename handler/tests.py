from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
import random   
from handler.utils.redis_op import RedisClient

User = get_user_model()

class HighLoadTransactionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test",
            password="password123"
        )

    def setUp(self):
        self.client = APIClient()
        self.client.login(
            username="test",
            password="password123"
        )
        self.redis = RedisClient().client

    def test_transactions(self):
        url = reverse("datarecord-upload")
        requests_amount = 1000

        payloads = []

        # مرحله 1: ارسال داده‌ها
        for _ in range(requests_amount):
            payload = {
                "data": random.randint(1, 1000),
                "date": timezone.now().isoformat()
            }
            payloads.append(payload)
            response = self.client.post(url, payload, format="json")
            self.assertIn(response.status_code, [200, 201, 202])

        # مرحله 2: بررسی Redis
        queue_length = self.redis.llen("db_queue")
        self.assertEqual(queue_length, requests_amount)

        # # # مرحله 3: اجرای تسک بولک به صورت سینک
        # # flush_db_queue()

        # # مرحله 4: بررسی دیتابیس
        # db_count = DataRecord.objects.filter(
        #     user=self.user
        # ).count()
        # self.assertEqual(db_count, requests_amount)

        # # مرحله 5: Redis باید خالی شده باشه
        # queue_length_after = self.redis.llen("db_queue")
        # self.assertEqual(queue_length_after, 0)
