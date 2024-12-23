from django.urls import path
from . import views

urlpatterns = [
    path('filter_data_file_review/', views.filter_data_file_review, name='filter_data_file_review'),
    path('generate_graphs/', views.generate_graphs, name='generate_graphs'),
]