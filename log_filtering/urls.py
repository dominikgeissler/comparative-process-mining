from django.urls import path
from . import views

urlpatterns = [
    path('', views.log_filter, name="log_filter"),
    path('show', views.show_logs, name="log_list")
    ]
