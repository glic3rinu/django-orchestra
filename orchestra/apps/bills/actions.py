from django.http import HttpResponse

from orchestra.utils.system import run


def generate_bill(modeladmin, request, queryset):
    bill = queryset.get()
    bill.close()
    return HttpResponse(bill.html)
    pdf = run('xvfb-run -a -s "-screen 0 640x4800x16" '
        'wkhtmltopdf --footer-center "Page [page] of [topage]" --footer-font-size 9 - -',
        stdin=bill.html.encode('utf-8'), display=False)
    return HttpResponse(pdf, content_type='application/pdf')
