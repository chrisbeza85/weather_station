import os
from django.urls import path
from . import views
from pathlib import Path
from django.conf import settings
from django.conf.urls.static import static
from .views import scan_qr_codes

urlpatterns = [
    path('environment/', views.display_environment, name='display_environment'),
    path('test/', views.test_view, name='test_view'),
    path('sensors/temperature/', views.temperature_data, name='temperature_data'),
    path('sensors/temperature/get/', views.get_sensor_data, name='get_sensor_data'),  # For GET requests
    path('temperature/', views.record_data, name='record_data'),  # For POST requests, if separate
    path('display/', views.display_data, name='display_data'),
    path('api/sensors/latest/', views.latest_data, name='latest_data'),
    path('api/sensors/history/', views.history_data, name='history_data'),
    path('relay-control/', views.relay_control, name='relay_control'),
    path('', views.item_list, name='item_list'),
    path('add/', views.item_add, name='item_add'),
    path('<int:pk>/', views.item_detail, name='item_detail'),
    path('<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('scan/', views.scan_item, name='scan_item'),
    path('qr-scan/', views.qr_scan, name='qr_scan'),
    path('qr-scan2/', views.qr_scan2, name='qr_scan2'),
    path('scan-qr/', views.scan_qr_code, name='scan_qr_code'),
    path('scan-student/', views.scan_student, name='scan_student'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'), # nah
    path('attendance_list/', views.attendance_list, name='attendance_list'), # nah
    path('students/', views.student_list, name='student_list'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/add/', views.student_add_edit, name='student_add_edit'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('scan_qr_codes/', scan_qr_codes, name='scan_qr_codes'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
