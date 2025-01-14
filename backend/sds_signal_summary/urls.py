from django.urls import path
from .views import filter_signal_summary

urlpatterns = [
    path('filter_signal_summary/', filter_signal_summary, name='filter_signal_summary'),
    # path('filter_data_home_page2/', filter_data_home_page2, name='filter_data_home_page2'),


]