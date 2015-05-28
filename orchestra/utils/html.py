import textwrap

from orchestra.utils.sys import run


def html_to_pdf(html, pagination=False):
    """ converts HTL to PDF using wkhtmltopdf """
    print(pagination)
    context = {
        'pagination': textwrap.dedent("""\
            --footer-center "Page [page] of [topage]"\\
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
            --margin-top 20 - -\
        """) % context
    return run(cmd, stdin=html.encode('utf-8')).stdout
