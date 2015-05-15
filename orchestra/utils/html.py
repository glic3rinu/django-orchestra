import textwrap

from orchestra.utils.sys import run


def html_to_pdf(html):
    """ converts HTL to PDF using wkhtmltopdf """
    return run(textwrap.dedent("""\
        PATH=$PATH:/usr/local/bin/
        xvfb-run -a -s "-screen 0 2480x3508x16" wkhtmltopdf -q \\
            --use-xserver \\
            --footer-center "Page [page] of [topage]" \\
            --footer-font-name sans \\
            --footer-font-size 7 \\
            --footer-spacing 7 \\
            --margin-bottom 22 \\
            --margin-top 20 - - """),
        stdin=html.encode('utf-8')
    ).stdout
