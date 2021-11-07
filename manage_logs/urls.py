from django.urls import path
from . import views

urlpatterns = [
    path('', views.ManageLogs.as_view()),
    ]
