from django.urls import path
from . import views

urlpatterns = [
    path('filter_claim_leakage', views.filter_claim_leakage, name='filter_claim_leakage'),
    path('generate_graphs', views.generate_graphs, name='generate_graphs'),
    # path('filter_data_ai_accuracy', views.filter_data_ai_accuracy, name='filter_data_ai_accuracy'),
]