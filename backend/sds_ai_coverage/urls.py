from django.urls import path
from . import views

urlpatterns = [
   
    path('filter_data_ai_coverage', views.filter_data_ai_coverage, name='filter_data_ai_accuracy'),
    path('ai_coverage_view', views.ai_coverage_view, name='ai_coverage'),
]