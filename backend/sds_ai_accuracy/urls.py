from django.urls import path
from . import views

urlpatterns = [
    path('', views.ai_accuracy_view, name='ai_accuracy'),
    path('filter_data_ai_accuracy', views.filter_data_ai_accuracy, name='filter_data_ai_accuracy'),
]