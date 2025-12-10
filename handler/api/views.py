from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    CreateDataRecordSerializer,
    SwingAnalyzerSerializer
)


class DataRecordCreateView(generics.CreateAPIView):
    """
    DataRecordCreateView that handles creation of DataRecord instances
    """
    serializer_class = CreateDataRecordSerializer
    permission_classes = [IsAuthenticated]
class SwingAnalyzerView(generics.GenericAPIView):
    """
    SwingAnalyzerView that handles GET requests to analyze data using swing trade algorithm
    """
    serializer_class = SwingAnalyzerSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)