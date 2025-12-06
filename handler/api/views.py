from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from handler.models import DataRecord
from .serializers import (
    ListDataRecordSerializer,
    CreateDataRecordSerializer,
    DetailDataRecordSerializer
)

class DataRecordListView(generics.ListAPIView):
    serializer_class = ListDataRecordSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.user.is_superuser:
            return DataRecord.objects.all()
        return DataRecord.objects.filter(user=self.request.user)
class DataRecordCreateView(generics.CreateAPIView):
    serializer_class = CreateDataRecordSerializer
    permission_classes = [IsAuthenticated]
class DataRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DetailDataRecordSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if self.request.user.is_superuser:
            return DataRecord.objects.all()
        return DataRecord.objects.filter(user=self.request.user)