from django.urls import path
from . import views

urlpatterns = [
    path('environment/', views.display_environment, name='display_environment'),
    path('test/', views.test_view, name='test_view'),
    path('sensors/temperature/', views.temperature_data, name='temperature_data'),
    path('sensors/temperature/get/', views.get_sensor_data, name='get_sensor_data'),  # For GET requests
    path('temperature/', views.record_data, name='record_data'),  # For POST requests, if separate
    path('display/', views.display_data, name='display_data'),
    path('api/sensors/latest/', views.latest_data, name='latest_data'),
    path('api/sensors/history/', views.history_data, name='history_data'),
]
