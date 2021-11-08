# URLconf
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from .models import Log, LogObjectHandler
from helpers.g6_helpers import dfg_dict_to_g6
from helpers.dfg_helper import convert_dfg_to_dict
import json
from os import remove
from os.path import join
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

# default
class Home(View):
    template_name = 'home.html'
    def get(self, request):
        return render(request, self.template_name)

class LogsJsonView(View):
    """
    S
    """
    def get(self, request, *args, **kwars):
        if 'id' in request.GET:
            id = int(request.GET['id'])
            return JsonResponse({"result":[Log.objects.filter(id=id)[0].to_dict()]})
        else: 
            return JsonResponse({"result":[ log.to_dict() for log in Log.objects.all() ]})

class CompareLogsJson(View):
    def get(self, request, *args, **kwars):
        #extract the pks/ids from the query url
        nr_of_comparisons = int(request.GET['nr_of_comparisons'])
        pks = [ request.GET[f'log{i}'] for i in range(1, nr_of_comparisons+1)]
        logs = [ LogObjectHandler(Log.objects.get(pk=pk)).to_dict() for pk in pks ]

        return JsonResponse({'logs': logs})

class CompareLogs(TemplateView):
    template_name = 'compare.html'

    def get(self, request, *args, **kwars):
        #extract the pks/ids from the query url
        nr_of_comparisons = int(request.GET['nr_of_comparisons'])
        pks = [ request.GET[f'log{i}'] for i in range(1, nr_of_comparisons+1)]
        logs = [ LogObjectHandler(Log.objects.get(pk=pk)).to_dict() for pk in pks ]

        js_data = {'graphs': [log['g6'] for log in logs]}
        js_data = json.dumps(js_data)
        return render(request, self.template_name, {'logs': logs, 'js_data': js_data})

class SelectLogs(TemplateView):
    template_name = 'select_logs.html'
    def get(self, request, *args, **kwars):
        logs = Log.objects.all()
        return render(request, self.template_name, {'logs': logs})

class ManageLogs(View):
    template_name = 'manage_logs.html'
    def get(self, request, *args, **kwars):
        logs = Log.objects.all()
        return render(request, self.template_name, {'logs': logs})

    def post(self, request, *args, **kwars):
        context = {}
        #we use a hidden field 'action' to determine if the post is used to delete a log or upload a new one
        if request.POST['action'] == 'delete':
            pks = request.POST.getlist('pk')
            logs =  Log.objects.filter(pk__in=pks)
            for log in logs:
                remove(join(settings.EVENT_LOG_URL, log.log_name))
            logs.delete()
        elif request.POST['action'] == 'upload':
            file = request.FILES['log_file']
            validator = FileExtensionValidator(['csv', 'xes'])
            try:
                validator(file)
            except ValidationError:
                return render(request, self.template_name, {'logs': Log.objects.all(), 'error': 'file extension not supported'})
            log = Log(
                log_file=file,
                log_name=file.name)
            log.save()

        context['logs'] = Log.objects.all()
        context['message'] = 'Upload successful' if request.POST['action'] == 'upload' else 'Successfuly deleted'
        return render(request, self.template_name, context)

def graph_example(request,id):
    handler = LogObjectHandler(Log.objects.get(id=id))
    dfg = handler.generate_dfg()
    res =  dfg_dict_to_g6(convert_dfg_to_dict(dfg))
    data = json.dumps(res)
    return {'div_id': 'left', 'data':data}