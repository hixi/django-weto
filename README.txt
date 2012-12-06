Warning
-------

This is not stable software, and comes without any warranties - use at own risk.

Why this name?
--------------

it is short, and not already taken - and most importantly, will most likely not be taken anytime soon ;-)


What is this?
-------------

``django-weto`` despite its simplicity has the pompous mission of automagically
converting on-the-fly views' HTML output to PDF --without modifying your views.

It has originally been developed by ``directeur`` https://github.com/directeur/django-pdf,
forked from there and altered to work with wkhtmltopdf.


Requirements
------------

django-weto depends on wkhtmltopdf:
http://code.google.com/p/wkhtmltopdf/wiki/Usage


How to use django-weto
----------------------------

There are really 4 steps to setting it up with your projects.
0. Install this tiny app into you environment, ie (using virtualenv):
    pip install https://github.com/hixi/django-pdf/tarball/master#egg=django-weto-0.1-alpha-3

1. List this application in the ``INSTALLED_APPS`` portion of your settings
   file.  Your settings file might look something like::
   
       INSTALLED_APPS = (
           # ...
           'weto',
       )

2. Install the pdf middleware. Your settings file might look something
   like::
   
       MIDDLEWARE_CLASSES = (
           # ...
           'weto.middleware.PdfMiddleware',
       )

3. If it's not already added in your setup, add the request context processor.
   Note that context processors are set by default implicitly, so to set them
   explicitly, you need to copy and paste this code into your under
   the value TEMPLATE_CONTEXT_PROCESSORS::
   
        ("django.core.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.request")

4. Add the django_pdf's context processor

    TEMPLATE_CONTEXT_PROCESSORS=(
        "django.core.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.request", #<-- this line is necessary to access request in template tags
        "weto.context_processors.check_format", #<-- this line
    )

That's it, now all it takes to generate a PDF version of your page is to add:
?format=pdf to your urls

Example:
    http://127.0.0.1/contacts/list displays Contacts' list.
    http://127.0.0.1/contacts/list?format=pdf returns the pdf version of it.


You may ask: "Wait! what if I don't want to include some parts of the HTML page
in the PDF output? (like a menu)" 
You'd be right, and the answer is easy:
Use the variable DJANGO_PDF_OUTPUT in your template which will be set to True if
the PDF is requested and to False otherwise.

Example:
    {% if not DJANGO_PDF_OUTPUT %}
        <ul id="menu">
            <li>menu item</li>
            <li>menu item</li>
            <li>menu item</li>
        </ul>
    {% endif %}

Also, you can use {% if DJANGO_PDF_OUTPUT %} to include some parts only in the
PDF output.


Bonus:
-------

You have a new template tag {% pdf_link %} which will generate a link to the PDF
version of the current page. :)

P.S.

The string "format=pdf" and the variable DJANGO_PDF_OUTPUT are customizable in
your settings.

Look:

WETO_REQUEST_FORMAT_NAME = getattr(settings, 'REQUEST_FORMAT_NAME', 'format')
WETO_REQUEST_FORMAT_PDF_VALUE = getattr(settings, 'REQUEST_FORMAT_PDF_VALUE', 'pdf')
WETO_TEMPLATE_PDF_CHECK = getattr(settings, 'TEMPLATE_PDF_CHECK',
'DJANGO_PDF_OUTPUT')

That's it!  

# TODO: Write better doc.
