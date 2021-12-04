# URLconf
from genericpath import isfile
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from .models import Log, LogObjectHandler
from os import remove
import errno
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

class CompareLogs(TemplateView):
    """
    Comparison page
    used to compare different event logs
    """
    
    template_name = 'compare.html'

    def get(self, request, *args, **kwars):
        """returns the logs selected by the user and the rendered graph"""
        # extract the pks/ids from the query url
        nr_of_comparisons = int(request.GET['nr_of_comparisons'])
        ids = [request.GET[f'log{i}'] for i in range(1, nr_of_comparisons + 1)]
        ref = int(request.GET['ref'])
        logs = [Log.objects.get(pk=id) for id in ids]
        handlers_pk = []
        for log in logs:
            if LogObjectHandler.objects.filter(log_object=log).exists():
                handler = LogObjectHandler.objects.get(log_object=log)
            else:
                handler = LogObjectHandler(log_object=log)
                handler.save()
            handlers_pk.append(handler.pk)
        handlers = [LogObjectHandler.objects.get(pk=id) for id in handlers_pk]
        debug = [handler.__dict__ for handler in handlers]
        return render(request, self.template_name, {"logs": handlers, 'ref': ref, "debug": debug})

    


class SelectLogs(TemplateView):
    """
    Select Logs from
    used to select the logs for comparison
    """
    template_name = 'select_logs.html'

    def get(self, request, *args, **kwars):
        """returns all uploaded logs"""
        logs = Log.objects.all()
        return render(request, self.template_name, {'logs': logs})


class ManageLogs(View):
    """
    Manage Logs page
    used for uploading and deleting logs
    """
    template_name = 'manage_logs.html'

    def get(self, request, *args, **kwars):
        """returns all uploaded log files"""
        # get logs from database
        logs = Log.objects.all()

        # get shadow objects
        # (objects that are still in the database but not linked to a file)
        not_local_logs = Log.objects.filter(pk__in=[
            log.pk for log in logs if not isfile(log.log_file.path)
        ])

        # if any exist, delete them and refresh
        if not_local_logs:
            not_local_logs.delete()
            logs = Log.objects.all()

        return render(
            request, self.template_name, {
                'logs': logs})

    def post(self, request, *args, **kwars):
        """either uploads or delete a already uploaded log"""
        context = {}
        # we use a hidden field 'action' to determine if the post is used to
        # delete a log or upload a new one
        if request.POST['action'] == 'delete':
            if not request.POST.getlist('pk'):
                return render(
                    request, self.template_name, {
                        'logs': Log.objects.all(), 'error': 'Please select a log'})

            pks = request.POST.getlist('pk')
            logs = Log.objects.filter(pk__in=pks)
            for log in logs:
                try:
                    # remove local files in media/logs
                    remove(log.log_file.path)
                except OSError as e:
                    # if error is not FileNotFound, raise it
                    # otherwise ignore
                    if e.errno != errno.ENOENT:
                        raise
            # remove the log out of the database
            logs.delete()
        else: 
            if not request.FILES:
                return render(
                    request, self.template_name, {
                        'logs': Log.objects.all(), 'error': 'Please add a log'})
            # get the log file from file form
            file = request.FILES['log_file']
            # validate the extension
            validator = FileExtensionValidator(['csv', 'xes'])
            try:
                validator(file)
            except ValidationError:
                return render(
                    request, self.template_name, {
                        'logs': Log.objects.all(), 'error': 'file extension not supported'})
            # create a new Log object
            log = Log(
                log_file=file,
                log_name=file.name)
            # save the log in the database
            log.save()
        # return all uploaded logs and message depending on action taken
        context['logs'] = Log.objects.all()
        context['message'] = 'Upload successful' if request.POST['action'] == 'upload' else 'Successfuly deleted'
        return render(request, self.template_name, context)


class FilterView(View):
    """
    Manage Logs page
    used for uploading and deleting logs
    """

    def get(self, request, *args, **kwars):
        import json
        data = json.loads(request.GET['data'])
        id,_,attr = data["attribute"].strip().split("-")
        perc_filter = data["percentage_filter"]
        handler = LogObjectHandler.objects.get(pk=id)
        # create filter

        handler.set_filter("percentage", perc_filter)

        return JsonResponse({"response": "Ok"})
