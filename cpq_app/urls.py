from django.urls import path, include
from cpq_app import views

urlpatterns = [
    path('', views.sample_view, name='sample_view')
]