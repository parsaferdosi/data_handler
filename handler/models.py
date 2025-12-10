from django.db import models
from django.contrib.auth import get_user_model
User=get_user_model()
class DataRecord(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    data=models.IntegerField(null=False, blank=False)
    date=models.DateTimeField(null=False, blank=False)
    