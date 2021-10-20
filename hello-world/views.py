import json
from django.http import HttpResponse

def hello_world(request):
    json_response = {"message": "Hello World"}
    return HttpResponse(json.dumps(json_response), content_type="application/json")