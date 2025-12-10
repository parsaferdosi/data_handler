from django.db import models
from django.contrib.auth import get_user_model
User=get_user_model()
"""
  data model for storing data records associated with users  
"""
class DataRecord(models.Model):
    """
    Docstring for DataRecord
    DataRecord model to store data associated with a user and a timestamp
    user: ForeignKey to User model
    data: IntegerField to store the data value
    date: DateTimeField to store the timestamp of the data record
    """
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    data=models.IntegerField(null=False, blank=False)
    date=models.DateTimeField(null=False, blank=False)
    