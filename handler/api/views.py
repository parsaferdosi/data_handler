from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    CreateDataRecordSerializer,
)


class DataRecordCreateView(generics.CreateAPIView):
    serializer_class = CreateDataRecordSerializer
    permission_classes = [IsAuthenticated]
