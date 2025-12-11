import json
import random

from django.test import TransactionTestCase, Client 
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from asgiref.sync import sync_to_async 

# ----------------------------
# A fully internal Django Test Case using TransactionTestCase for stability
# ----------------------------
# CHANGED BASE CLASS
class DataUploadInternalTest(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    # NOTE: Since we use TransactionTestCase, we must manually clean up created objects
    # if we want to reuse the same data across tests (though not necessary here).

    def setUp(self):
        # 1. User setup and authentication (SYNC)
        self.username = "parsa_test"
        self.password = "admin_test"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )
        self.client = Client()
        self.client.force_login(self.user) 

        # 2. Test data setup
        self.payload_count = 1000
        self.payloads = []
        self.time_now = timezone.now()
        self.initial_time = self.time_now

        for _ in range(self.payload_count):
            self.time_now += timezone.timedelta(minutes=1)
            random_data = random.randint(1, 100) 
            self.payloads.append({
                "date": self.time_now.isoformat(),
                "data": random_data
            })
        
        # 3. Async Wrapper for synchronous helpers (ESSENTIAL)
        # Note: 'thread_sensitive=True' is crucial for DB access in sync code
        self._send_all_payloads_async = sync_to_async(self._send_all_payloads, thread_sensitive=True)
        self._check_swing_analysis_async = sync_to_async(self._check_swing_analysis, thread_sensitive=True)


    # Helper method for synchronous HTTP POST requests (SYNC)
    def _send_all_payloads(self):
        """Sends all data payloads using the synchronous Django test client."""
        upload_url = reverse("datarecord-upload") 
        
        for p in self.payloads:
            response = self.client.post(
                upload_url,
                data=json.dumps(p),
                content_type="application/json"
            )
            self.assertEqual(response.status_code, 201, msg=f"Failed for payload {p}")

    def _check_swing_analysis(self):
        """Checks the swing analysis endpoint using the synchronous Django test client."""
        
        start_time_str = self.initial_time.replace(microsecond=0).isoformat().replace('+00:00', '')
        end_time_str = self.time_now.replace(microsecond=0).isoformat().replace('+00:00', '')
        
        analyze_url = reverse("swing-analyze")
        
        # Example format now: 2025-12-11T08:14:31
        query_string = f"?start_time={start_time_str}&end_time={end_time_str}"
        
        resp = self.client.get(
            f"{analyze_url}{query_string}" 
        )
        
        if resp.status_code != 200:
            error_message = f"Assertion failed: Expected 200 but got {resp.status_code}. "
            try:
                error_details = resp.json()
                error_message += f"Response JSON: {error_details}"
            except json.JSONDecodeError:
                error_message += f"Response Content: {resp.content.decode()}"
            
            self.fail(error_message)
        
        self.assertEqual(resp.status_code, 200) 
        data = resp.json() 
        self.assertIsInstance(data, dict)
    # Main async test method
    async def test_upload(self):
        await self._send_all_payloads_async()
        # ----------------------------
        # 4. Final swing analysis (SYNC executed ASYNC)
        # ----------------------------
        await self._check_swing_analysis_async()