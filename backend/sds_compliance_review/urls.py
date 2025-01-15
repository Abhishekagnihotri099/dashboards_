from django.urls import path
from . import views

urlpatterns = [
    path('filter_compliance_review', views.filter_compliance_review, name='filter_compliance_review'),
    # path('filter_data_ai_accuracy', views.filter_data_ai_accuracy, name='filter_data_ai_accuracy'),
]