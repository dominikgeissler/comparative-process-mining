from django.urls import path
from django.views.generic.base import TemplateView
from .views import Home, ManageLogs, SelectLogs, CompareLogs
# from .views import LogsJsonView, CompareLogsJson

urlpatterns = [
    path('', Home.as_view(), name="home_view"),
    path('manage', ManageLogs.as_view(), name="manage_view"),
    path('comp', TemplateView.as_view(
        template_name='select_comparisons.html'), name="select_comp_view"),
    path('select_logs', SelectLogs.as_view(), name="select_log_view"),
    path('compare', CompareLogs.as_view(), name="compare_log_view"),
    #path('logs', LogsJsonView.as_view()),
    #path('json/compare', CompareLogsJson.as_view()),
    #path('comp', TemplateView.as_view(template_name='select_comparisons.html')),
]
