from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from os import listdir
from os.path import join, isfile
from django.views.generic.base import View, TemplateView
from manage_logs.models import Log, LogObjectHandler

event_log_path = settings.EVENT_LOG_URL

class ManageLogs(View):
    template_name = "manage_logs.html"
    def get(self, request):
        logs = Log.objects.all()
        return render(request, self.template_name, {'logs': logs})
    def post(self, request):
        pass