from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.DataRecordListView.as_view(), name='datarecord-list-create'),
    path('data/upload/', views.DataRecordCreateView.as_view(), name='datarecord-upload'),
    path('data/<int:pk>/', views.DataRecordDetailView.as_view(), name='datarecord-detail'),
]