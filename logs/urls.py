from django.urls import path
from django.views.generic.base import TemplateView
from .views import ManageLogs, LogsJsonView,SelectLogs, CompareLogs, CompareLogsJson

urlpatterns = [ 
    path('manage', ManageLogs.as_view()),
    path('logs', LogsJsonView.as_view()),
    path('select_comparisons',TemplateView.as_view(template_name='select_comparisons.html')),
    path('select_logs',SelectLogs.as_view()),
    path('compare', CompareLogs.as_view()),
    path('json/compare', CompareLogsJson.as_view()),
    path('',TemplateView.as_view(template_name='select_comparisons.html'))
]

