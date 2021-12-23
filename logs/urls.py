from django.urls import path
from django.views.generic.base import TemplateView
from .views import ManageLogs, SelectLogs, CompareLogs

urlpatterns = [
    path('', ManageLogs.as_view(), name="manage_view"),
    path('user_manual', TemplateView.as_view(
        template_name="user_manual.html"
    ), name="user_manual_view"),
    path('comp', TemplateView.as_view(
        template_name='select_comparisons.html'), name="select_comp_view"),
    path('select_logs', SelectLogs.as_view(), name="select_log_view"),
    path('compare', CompareLogs.as_view(), name="compare_log_view"),
    path(r"^ajax/responsefilter/$", CompareLogs.filter, name="update_filter"),
    path(r"^ajax/blabla/$", CompareLogs.download, name="download_comparison")
    
]
