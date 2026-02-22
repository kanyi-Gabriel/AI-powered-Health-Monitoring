from django.urls import path
from . import views

urlpatterns = [
    # This catches the exact path the ESP32 is looking for
    path('upload-vitals/', views.process_sensor_data, name='process_sensor_data'),
]