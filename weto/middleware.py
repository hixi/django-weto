#!/usr/bin/env python
from tempfile import NamedTemporaryFile
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils import translation
import re, subprocess
import cStringIO as StringIO
from django.conf import settings

WETO_REQUEST_FORMAT_NAME = getattr(settings, 'WETO_REQUEST_FORMAT_NAME', 'format')
WETO_REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'WETO_REQUEST_FORMAT_PDF_VALUE', 'pdf')
WETO_LIB_PATH = getattr(settings, 'WETO_LIB_PATH', '/usr/bin/wkhtmltopdf')
WETO_OPTS = getattr(settings, 'WETO_OPTS', ["--dpi", "600", "--page-size", "A4"])
DEBUG = getattr(settings, 'DEBUG', False)

def replace_relative_with_absolute_links(site_url, content):
    #    replace urls with absolute urls including site and ssl/non-ssl
    content = re.sub(r'href="/', r'href="%s/' % site_url, content)
    content = re.sub(r'src="/', r'src="%s/' % site_url, content)
    #    replace relative urls with absolute urls including site and ssl/non-ssl,
    #    not sure if this really works this way...
    content = re.sub(r'href="!http', r'href="%s/' % site_url, content)
    content = re.sub(r'src="!http', r'src="%s/' % site_url, content)
    return content

def transform_to_pdf(response, request):
    toc = request.GET.get("toc", None)
    footer = request.GET.get("footer", None)
    header = request.GET.get("header", None)
    pdf_name = request.GET.get("pdf_name", "report.pdf")
    response['mimetype'] = 'application/pdf'
    response['Content-Disposition'] = 'attachment; filename=%s.pdf' % pdf_name
    content = response.content
    # TODO: Make this more stable and less a hack
    site_url =  u"https://" if request.is_secure() else u"http://"
    current_site = Site.objects.get_current()
    site_url += current_site.domain
    site_url = str(site_url)
    content = replace_relative_with_absolute_links(site_url, content)
    string_content = StringIO.StringIO(content)
    popen_command = [WETO_LIB_PATH,] + WETO_OPTS
    language = translation.get_language()
    if header:
        header_file = NamedTemporaryFile(suffix='.html')
        header = render_to_string('weto/pdf_header.html', request)
        header_file.write(replace_relative_with_absolute_links(site_url, header))
        header_file.flush()
        header_file.seek(0)
        popen_command += ['--header-html', header_file.name]
    if footer:
        footer_file = NamedTemporaryFile(suffix='.html')
        footer = render_to_string('weto/pdf_footer.html', request)
        footer_file.write(replace_relative_with_absolute_links(site_url, footer))
        footer_file.flush()
        footer_file.seek(0)
        popen_command += ['--footer-html', footer_file.name]
    if toc:
        toc_file = NamedTemporaryFile()
        popen_command += ["toc"]
        if toc != "default":
            rendered = render_to_string('weto/toc_xsl.xml', request)
            if getattr(settings, 'USE_I18N'):
                toc_file.write(rendered.translate(language))
            else:
                toc_file.write(rendered)
            toc_file.flush()
            toc_file.seek(0)
            popen_command += ['--xsl-style-sheet', toc_file.name]
    popen_command += [ "-", "-"]
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
    string_content.close()
    # don't know why, but I need to first remove the content, before writing to it, else it appends the content
    response.content = ''
    response.write(pdf[0])
    if header:
        header_file.close()
    if toc:
        toc_file.close()
    if footer:
        footer_file.close()
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