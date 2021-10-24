from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def upload_page(request):
    # if user wants to upload a file
    if request.method == 'POST' and request.FILES['upload_file']:
        # get file from form
        file = request.FILES['upload_file']
        # create new FileSystemStorage
        fs = FileSystemStorage()
        # save file and get filename
        filename = fs.save(file.name, file)
        # get file url
        file_url = fs.url(filename)
        # return file url
        return render(request, 'upload_page.html', {'file_url': file_url})
    # return empty page
    return render(request, 'upload_page.html')
