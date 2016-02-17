import textwrap

from django.templatetags.static import static
from django.utils.translation import ugettext_lazy as _

from orchestra.utils.sys import run


def html_to_pdf(html, pagination=False):
    """ converts HTL to PDF using wkhtmltopdf """
    context = {
        'pagination': textwrap.dedent("""\
            --footer-center "Page [page] of [topage]" \\
            --footer-font-name sans \\
            --footer-font-size 7 \\
            --footer-spacing 7"""
        ) if pagination else '',
    }
    cmd = textwrap.dedent("""\
        PATH=$PATH:/usr/local/bin/
        xvfb-run -a -s "-screen 0 2480x3508x16" wkhtmltopdf -q \\
            --use-xserver \\
            %(pagination)s \\
            --margin-bottom 22 \\
            --margin-top 20 - - \
        """) % context
    return run(cmd, stdin=html.encode('utf-8')).stdout


def get_on_site_link(url):
    context = {
        'title': _("View on site %s") % url,
        'url': url,
        'image': '<img src="%s"></img>' % static('orchestra/images/view-on-site.png'),
    }
    return '<a href="%(url)s" title="%(title)s">%(image)s</a>' % context
