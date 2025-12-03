from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
User=get_user_model()
# Create your tests here.
class SimpleTest(APITestCase):
    def setUp(self):
        self.test_user=User.objects.create_user(username='testuser',password='testpass')
        self.client.force_authenticate(user=self.test_user)
        self.url=reverse('datarecord-upload')
    def test_user_creation(self):
        response=self.client.post(self.url,{'weight':70,'height':175})
        self.assertEqual(response.status_code,201)
        self.assertIn('weight',response.data)
        self.assertIn('height',response.data)