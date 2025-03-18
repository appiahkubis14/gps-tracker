from django.urls import path
from .views import parse_gps_data

urlpatterns = [
    path('gps/latest/<str:imei>/', parse_gps_data, name='latest_gps_data'),
]
