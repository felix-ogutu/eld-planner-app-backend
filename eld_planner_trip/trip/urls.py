from django.urls import path
from .import views

urlpatterns = [
    path('calculate-trip/',views.calculate_trip,name='calculate_trip'),
    path('generate-eld-log/',views.generate_eld_log,name='generate_eld_log'),
]

