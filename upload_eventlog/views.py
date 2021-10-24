from django.shortcuts import render

def upload_page(request):
    return render(request, 'upload_page.html', {'message': 'Hallo'})
