from django.urls import path
from .views import get_leakage_data, get_file_review_data

urlpatterns = [
    path('api/filtered-data-leakage/', get_leakage_data, name='filtered_data'),
    path('api/filtered-data-filereview/', get_file_review_data, name='filtered_data'),
]