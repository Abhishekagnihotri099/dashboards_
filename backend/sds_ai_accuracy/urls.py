from django.urls import path
from . import views

urlpatterns = [
    path('', views.ai_accuracy_view, name='ai_accuracy'),
]