import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

import secrets, io
from base64 import b64decode
from PIL import Image
from django.core.files.base import ContentFile

def get_image_from_data_url(data_url, resize=True, base=600):
        _format, _url = data_url.split(';base64,')
        _filename = secrets.token_hex(20) 
        _ext = _format.split('/')[-1]
        filename = f"{_filename}.{_ext}"
        file = ContentFile(b64decode(_url), name=filename)
        
        if resize:
                image = Image.open(file)
                image_io = io.BytesIO()
                _perc = base/float(image.size[0])
                _size = int(float(image.size[1])* float(_perc))
                image = image.resize((base, _size), Image.ANTIALIAS)
                image.save(image_io, format=_ext)
                file = ContentFile(image_io.getvalue(), name=filename) 

        
        return file, filename

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

def render_pdf_view(template_path, context ):
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response