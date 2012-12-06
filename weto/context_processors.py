from django.conf import settings

WETO_REQUEST_FORMAT_NAME = getattr(settings, 'WETO_REQUEST_FORMAT_NAME', 'format')
WETO_REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'WETO_REQUEST_FORMAT_PDF_VALUE', 'pdf')
WETO_TEMPLATE_PDF_CHECK = getattr(settings, 'WETO_TEMPLATE_PDF_CHECK', 'DJANGO_PDF_OUTPUT')


def check_format(request):
    """
    Adds a TEMPLATE_PDF_CHECK variable to the context.
    This var will normally be used in templates like this:
    {% if DJANGO_PDF_OUTPUT %}
        ... content to be displayed only in the PDF output
    {% endif %}
    or:
    {% if not DJANGO_PDF_OUTPUT %}
        ... content that won't be displayed only in the PDF output
    {% endif %}

    Notice:
    Here the value of TEMPLATE_PDF_CHECK settings var is the default one, i.e.
    DJANGO_PDF_OUTPUT. You can change this in your settings
    """
    format = request.GET.get(WETO_REQUEST_FORMAT_NAME, None)
    if format == WETO_REQUEST_FORMAT_PDF_VALUE:
        return {WETO_TEMPLATE_PDF_CHECK: True}
    else:
        return {WETO_TEMPLATE_PDF_CHECK: False}
