from django.db import models
from django.contrib.auth import get_user_model
User=get_user_model()

class DataRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight=models.FloatField()
    height=models.FloatField()
    bmi=models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DataRecord {self.id} by {self.user.username} at {self.timestamp}"
    def save(self, *args, **kwargs):
        self.bmi = self.weight / ((self.height / 100) ** 2)
        super().save(*args, **kwargs)