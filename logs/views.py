# URLconf
from genericpath import isfile
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from .models import Log, LogObjectHandler, ComparisonMetrics, LogMetrics
from helpers.g6_helpers import dfg_dict_to_g6
from helpers.dfg_helper import convert_dfg_to_dict
import json
from os import remove, listdir
import errno
from os.path import join, basename
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

# default


class Home(View):
    """
    Home page
    First page the user will visit after starting the server
    """
    template_name = 'home.html'

    def get(self, request):
        """returns the home page template"""
        return render(request, self.template_name)

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
        logs = [Log.objects.get(pk=id) for id in ids]
        return render(request, self.template_name, {"logs": logs})


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
                    remove(join(settings.EVENT_LOG_URL, log.log_name))
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


class Metrics(View):
    template_name = "metrics.html"

    def get(self, request):
        """
        log, log2: two selected event logs to be compared
        Metrics calculation for comparative process mining via
        ComparisonMetrics(log.pm4py_log(), log2.pm4py_log())
        rendering of analyzed metrics for presentation in metrics.html
        """
        # get ids from query params
        first_id = request.GET['id1']
        second_id = request.GET['id2']

        # try parse to int
        try:
            first_id = int(first_id)
            second_id = int(second_id)
        except ValueError:
            # ids are no ints -> return
            return render(request, self.template_name, {'data': 'gib ids'})

        # try accessing the logs with given ids
        try:
            log = Log.objects.get(id=first_id)
            log2 = Log.objects.get(id=second_id)
        except Log.DoesNotExist:
            # log(s) with id does not exist
            return render(
                request, self.template_name, {
                    'data': 'Log with given ids do not exist'})

        # compare the two logs
        metrics = ComparisonMetrics(log.pm4py_log(), log2.pm4py_log())
        return render(
            request, self.template_name, {
                'data': metrics.get_comparison()})
