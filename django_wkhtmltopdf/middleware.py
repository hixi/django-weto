#!/usr/bin/env python
from django.contrib.sites.models import Site
import re, subprocess
import cStringIO as StringIO
from django.conf import settings

WETO_REQUEST_FORMAT_NAME = getattr(settings, 'WETO_REQUEST_FORMAT_NAME', 'format')
WETO_REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'WETO_REQUEST_FORMAT_PDF_VALUE', 'pdf')
WETO_LIB_PATH = getattr(settings, 'WETO_LIB_PATH', '/usr/bin/wkhtmltopdf')
WETO_OPTS = getattr(settings, 'WETO_OPTS', ["--dpi",
                                            "600",
                                            "--page-size",
                                            "A4"])
DEBUG = getattr(settings, 'DEBUG', False)

def transform_to_pdf(response, request):
    response['mimetype'] = 'application/pdf'
    response['Content-Disposition'] = 'attachment; filename=report.pdf'
    content = response.content
    # TODO: Make this more stable and less a hack
    site_url =  u"https://" if request.is_secure() else u"http://"
    current_site = Site.objects.get_current()
    site_url += current_site.domain
    site_url = str(site_url)
    #    replace urls with absolute urls including site and ssl/non-ssl
    content = re.sub(r'href="/', r'href="%s/' % site_url, content)
    content = re.sub(r'src="/', r'src="%s/' % site_url, content)
    #    replace relative urls with absolute urls including site and ssl/non-ssl,
    #    not sure if this really works this way...
    content = re.sub(r'href="!http', r'href="%s/' % site_url, content)
    content = re.sub(r'src="!http', r'src="%s/' % site_url, content)

    string_content = StringIO.StringIO(content)
    popen_command = [WETO_LIB_PATH,] + WETO_OPTS + [ "-", "-"]
    if DEBUG: # show errors on stdout
        sub = subprocess.Popen(popen_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
    else:
        sub = subprocess.Popen(popen_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    string_content.flush()
    string_content.seek(0)
    pdf = sub.communicate(input=string_content.read())
    response.write(pdf[0])
    return response


class PdfMiddleware(object):
    """
    Converts the response to a pdf one.
    """
    def process_response(self, request, response):
        format = request.GET.get(WETO_REQUEST_FORMAT_NAME, None)
        if format == WETO_REQUEST_FORMAT_PDF_VALUE:
            response = transform_to_pdf(response, request)
        return response