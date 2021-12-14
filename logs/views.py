# URLconf
from genericpath import isfile
from django.http import response
from django.http.response import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.generic.base import TemplateView, View
from .models import Filter, Log, LogObjectHandler
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
        nr_of_comparisons = int(request.GET.get('nr_of_comparisons', 2))
        ids = [int(request.GET.get(f'log{i}', 0)) for i in range(1, nr_of_comparisons + 1)]
        ref = int(request.GET.get('ref', 0))
        logs = [Log.objects.get(pk=id) for id in ids]
        # list of handlers
        handlers = []
        for log in logs:
            # get handler for log that aren't in the handler array
            # (refresh consistency and comparison between two
            # instances of same log)
            unique_handler_for_log = [handler for handler in LogObjectHandler.objects.filter(log_object=log) if handler not in handlers]
            # if a unique handler exists, select it
            if unique_handler_for_log:
                handler = unique_handler_for_log[0]
            else:
                # no unique handler exists -> create new one
                handler = LogObjectHandler.objects.create(log_object=log)
                handler.save()
            handlers.append(handler)            
        return render(
            request, self.template_name, {
                "logs": handlers, 'ref': ref})
    def download(self):
        import json
        from .utils import render_pdf_view
        imageURLs = json.loads(self.POST.get("imageURLs", []))
        ids = json.loads(self.POST.get("ids", []))
        ref = int(self.POST.get('ref', 0))
        handlers = [LogObjectHandler.objects.get(pk=int(id)) for id in ids ]
        context = {
            'names': [handler.log_name for handler in handlers],
            'isFrequency': [handler.get_isFrequency() for handler in handlers],
            'filters': [handler.get_filter() for handler in handlers],
            'graphs': imageURLs,
            'metrics': [handler.metrics(handlers[ref]) for handler in handlers],
            'similarity': [handler.get_similarity_index(handlers[ref]) for handler in handlers]
        }

        return render_pdf_view('to_pdf.html', context)
    
    def filter(self):
        import json
        data = json.loads(self.GET.get('data', ''))
        # check if the delete button was pressed
        if "delete" in data:
            # get the id of the LogObjectHandler from body
            id = data["delete"].split("-")[0]
            # get the handler
            handler = LogObjectHandler.objects.get(pk=id)
            # get the filter associated with the handler
            filter = Filter.objects.get(id=handler.filter_id)
            # delete the filter
            filter.delete()
            return JsonResponse({"success": True})
        # get id (from LogObjectHandler) and filter from body
        id,_,filter = data['type'].split("-")
        # get handler
        handler = LogObjectHandler.objects.get(pk=id)

        # remove the <id> from the values to refactor
        values = list(data.values())
        # since the filter given by the template is structured like
        # <id>-filtername
        # reset it to just the filtername
        values[0] = filter

        # set the filter
        handler.set_filter(list(data.keys()), values)

        # save the handler
        handler.save()
        return JsonResponse({'success': True})

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
