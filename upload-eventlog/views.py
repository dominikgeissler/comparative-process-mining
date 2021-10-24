from django.http import HttpResponse
from django.shortcuts import render

def upload_eventlog(request):
    return render(request, 'upload.html',{"message": "hi"})
