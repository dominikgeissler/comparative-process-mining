from django.urls import path
from django.views.generic.base import TemplateView
from .views import DownloadView, ManageLogs, SelectLogs, CompareLogs, FilterView

urlpatterns = [
    path('', ManageLogs.as_view(), name="manage_view"),
    path('about', TemplateView.as_view(
        template_name="about.html"
    ), name="about_view"),
    path('comp', TemplateView.as_view(
        template_name='select_comparisons.html'), name="select_comp_view"),
    path('select_logs', SelectLogs.as_view(), name="select_log_view"),
    path('compare', CompareLogs.as_view(), name="compare_log_view"),
    path(r'^ajax/get_response/$', FilterView.as_view(), name="update_filter"),
    path(r"^ajax/get_download/$", DownloadView.as_view(), name="download_comparison")
]
