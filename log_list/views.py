from django.shortcuts import render
from django.conf import settings
from os import listdir
from os.path import isfile, join

event_log_path = settings.EVENT_LOG_URL

def log_list(request):
    if request.method == "GET":
        return render(request, 'log_list.html', load_logs())
    return render(request, 'log_list.html')

def load_logs():
    return {'event_logs': [[file, join(event_log_path, file)] for file in listdir(event_log_path) if isfile(join(event_log_path, file))]}
