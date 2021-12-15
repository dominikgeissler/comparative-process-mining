import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from datetime import timedelta

# --- PDF ---

def link_callback(uri, rel):
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )

            return path

def render_pdf_view(template_path, context, image_urls=[]):
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    
    # remove temp images
    for img in image_urls:
        os.remove(img)
    
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# --- DFG ---

def convert_dfg_to_dict(dfg):
    dfg_graph_dict = {}
    min_frequency = float('inf')
    max_frequency = 0
    for (startnode, endnote), frequency in dfg.items():
        if startnode not in dfg_graph_dict:
            dfg_graph_dict[startnode] = {}
        dfg_graph_dict[startnode][endnote] = frequency
        min_frequency = min(min_frequency, frequency)
        max_frequency = max(max_frequency, frequency)

    dfg_properties = {
        'min_frequency': min_frequency,
        'max_frequency': max_frequency,
    }
    return {
        'properties': dfg_properties,
        'dfg_graph': dfg_graph_dict
    }

def dfg_dict_to_g6(dfg_dict):
    edges = []
    nodes = []
    dfg_graph_dict = dfg_dict['dfg_graph']
    unique_nodes = set()
    max_frequency = dfg_dict['properties']['max_frequency']
    min_frequency = dfg_dict['properties']['min_frequency']
    for startnode in dfg_graph_dict:
        edges_from_startnode = []
        unique_nodes.add(startnode)
        for endnode in dfg_graph_dict[startnode]:
            unique_nodes.add(endnode)
            frequency = dfg_graph_dict[startnode][endnode]
            edges_from_startnode.append(
                {
                    'source': startnode,
                    'target': endnode,
                    'label': frequency,
                    'style': {
                        # 'lineWidth': ((frequency - min_frequency) / (max_frequency - min_frequency)) * (18) + 2,
                        'endArrow': True
                    }
                }
            )
        edges.extend(edges_from_startnode)

    nodes = [
        {
            'id': node,
            'name': node,
            'isUnique': False,
            'conf': {
                'label': 'Name',
                'value': node,
            }


        }
        for node in unique_nodes
    ]
    return {
        'edges': edges,
        'nodes': nodes,
    }

# --- G6 ---

def highlight_nonstandard_activities(g6_graph, reference):
    """
    Highlight non-standard activities in dfg/g6-graph
    """
    """
    The log that is chosen first on the manage side or first uploaded
    will be the reference log for all comparisons
    """

    for node in g6_graph['nodes']:
        if find_node_in_g6(node['name'], reference):
            node['isUnique'] = 'False'
        else:
            node['isUnique'] = 'True'

    return g6_graph


def find_node_in_g6(node_name, reference):
    for node in reference['nodes']:
        if node['name'] == node_name:
            return True
    return False

# --- Metrics ---

def days_hours_minutes(total_seconds):
    """Transfer seconds format in days-hours-minutes-seconds format"""
    td = timedelta(seconds=total_seconds)
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds // 60) % 60
    seconds = td.seconds - hours * 3600 - minutes * 60
    return str(days) + "d "\
        + str(hours) + "h "\
        + str(minutes) + "m "\
        + str(seconds) + "s"


def get_difference(res1, res2):
    return [res1, str(res1 - res2) if res1 - res2 < 0 else "+" +
            str(res1 - res2) if res1 - res2 > 0 else "0"]


def get_difference_days_hrs_min(res1, res2):
    return [
        days_hours_minutes(res1),
        days_hours_minutes(
            res1 -
            res2) if res1 -
        res2 < 0 else "+" +
        days_hours_minutes(
            res1 -
            res2) if res1 -
        res2 > 0 else "0d"]
