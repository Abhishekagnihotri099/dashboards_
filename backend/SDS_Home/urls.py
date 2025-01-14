from django.urls import path
from .views import filter_data_home_page1, filter_data_home_page2

urlpatterns = [
    path('filter_data_home_page1/', filter_data_home_page1, name='filter_data_home_page1'),
    path('filter_data_home_page2/', filter_data_home_page2, name='filter_data_home_page2'),


]