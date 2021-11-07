from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from os import listdir
from os.path import join, isfile

event_log_path = settings.EVENT_LOG_URL

def manage_logs(request):
    # if user wants to upload a file
    if request.method == 'POST':
        if not request.FILES['upload_file']:
            return render(request, manage_logs.html, {'error': 'Pls select a file', 'event_logs': get_event_logs()})
        # get file from form
        file = request.FILES['upload_file']
        validator = FileExtensionValidator(['csv', 'xes'])
        try:
            validator(file)
        except ValidationError as error:
            return render(request, 'manage_logs.html', {'error': error, 'event_logs': get_event_logs()})
        # create new FileSystemStorage
        fs = FileSystemStorage(location=event_log_path, base_url=event_log_path)
        # save file and get filename
        filename = fs.save(file.name, file)
        # get file url
        file_url = fs.url(filename)
        # return file url
        return render(request, 'manage_logs.html', {'file_url': file_url, 'event_logs': get_event_logs()})
    # return empty page
    return render(request, 'manage_logs.html', {'event_logs': get_event_logs()})

def get_event_logs():
    return [[file, join(event_log_path, file)] for file in listdir(event_log_path) if isfile(join(event_log_path, file))]