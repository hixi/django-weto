from django import template
from django.conf import settings

register = template.Library()

WETO_REQUEST_FORMAT_NAME = getattr(settings, 'WETO_REQUEST_FORMAT_NAME', 'format')
WETO_REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'WETO_REQUEST_FORMAT_PDF_VALUE', 'pdf')


@register.simple_tag(name="pdf_link", takes_context=True)
def pdf_link(context, title, **kwargs):
    """
    Parses a tag that's supposed to be in one of the following format
     {% pdf_link title %}
     {% pdf_link title toc="Yes" %}
     {% pdf_link title header="Yes" %}
     {% pdf_link title header="Yes" footer="Yes" %}
     {% pdf_link title toc="Yes" footer="Yes" %}
     ...
    """
    toc = kwargs.get('toc', None)
    header = kwargs.get('header', None)
    footer = kwargs.get('footer', None)
    pdf_name = kwargs.get('pdf_name', None)
    request = context['request']
    getvars = request.GET.copy()
    getvars[WETO_REQUEST_FORMAT_NAME] = WETO_REQUEST_FORMAT_PDF_VALUE
    if toc:
        getvars['toc'] = "True"
    if header:
        getvars['header'] = "True"
    if footer:
        getvars['footer'] = "True"
    if pdf_name:
        getvars['pdf_name'] = pdf_name
    if len(getvars.keys()) > 1:
        urlappend = "&%s" % getvars.urlencode()
        urlappend = urlappend[1:]
    else:
        urlappend = '%s=%s' % (WETO_REQUEST_FORMAT_NAME, WETO_REQUEST_FORMAT_PDF_VALUE)

    url = '%s?%s' % (request.path, urlappend)
    return '<a href="%s" title="%s">%s</a>' % (url, title, title)
