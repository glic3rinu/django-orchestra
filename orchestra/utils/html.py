from orchestra.utils.sys import run


def html_to_pdf(html):
    """ converts HTL to PDF using wkhtmltopdf """
    return run(
        'PATH=$PATH:/usr/local/bin/\n'
        'xvfb-run -a -s "-screen 0 640x4800x16" '
            'wkhtmltopdf -q --footer-center "Page [page] of [topage]" '
            '   --footer-font-size 9 --margin-bottom 20 --margin-top 20 - -',
        stdin=html.encode('utf-8')
    ).stdout
