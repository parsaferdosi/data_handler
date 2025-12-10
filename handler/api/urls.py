from django.urls import path
from . import views

urlpatterns = [
    path('data/upload/', views.DataRecordCreateView.as_view(), name='datarecord-upload'),
]