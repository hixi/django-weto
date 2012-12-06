from django import template
from django.conf import settings

register = template.Library()

WETO_REQUEST_FORMAT_NAME = getattr(settings, 'WETO_REQUEST_FORMAT_NAME', 'format')
WETO_REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'WETO_REQUEST_FORMAT_PDF_VALUE', 'pdf')


@register.tag(name="pdf_link")
def pdf_link(parser, token):
    """
    Parses a tag that's supposed to be in this format: {% pdf_link title %}
    """
    try:
        tag_name, title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "pdf_link tag takes 1 argument"
    return PdfLinkNode(title)


class PdfLinkNode(template.Node):
    """
    Renders an <a> HTML tag with a link which href attribute
    includes the ?REQUEST_FORMAT_NAME=REQUEST_FORMAT_PDF_VALUE
    to the current page's url to generate a PDF link to the PDF version of this
    page.

    Eg.
        {% pdf_link PDF %} generates
        <a href="/the/current/path/?format=pdf" title="PDF">PDF</a>

    """
    def __init__(self, title):
        self.title = title

    def render(self, context):
        title = self.title
        if not (title[0] == title[-1] and title[0] in ('"', "'")):
            title = template.Variable(title).resolve(context)
        else:
            title = title[1:-1]
        request = context['request']
        getvars = request.GET.copy()
        getvars[WETO_REQUEST_FORMAT_NAME] = WETO_REQUEST_FORMAT_PDF_VALUE

        if len(getvars.keys()) > 1:
            urlappend = "&%s" % getvars.urlencode()
        else:
            urlappend = '%s=%s' % (WETO_REQUEST_FORMAT_NAME, WETO_REQUEST_FORMAT_PDF_VALUE)

        url = '%s?%s' % (request.path, urlappend)
        return '<a href="%s" title="%s">%s</a>' % (url, title, title)
