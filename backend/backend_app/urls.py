from django.urls import path
from . import views

urlpatterns = [
    path('filter_data_file_review/', views.filter_data_file_review, name='filter_data_file_review'),
    path('generate_graphs/', views.generate_graphs, name='generate_graphs'),
    #  path('claims_with_audit/', views.claims_with_audit_json, name='claims_with_audit_json'),
]

