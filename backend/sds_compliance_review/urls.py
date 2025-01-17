from django.urls import path
from .views import filter_compliance_review

urlpatterns = [
    path('filter_compliance_review/', filter_compliance_review, name='filter_compliance_review'),


]