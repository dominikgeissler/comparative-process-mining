from django.core import validators
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat
from os import listdir
from os.path import isfile, join


def log_filter(request):

    return render(request, 'log_filter.html')

def show_logs(request):
    if request.method == "GET":
        data = [file for file in listdir(settings.MEDIA_ROOT) if isfile(join(settings.MEDIA_ROOT, file))]
        return render(request, 'log_filter.html', {'data': data})
    return render(request, 'log_filter.html')