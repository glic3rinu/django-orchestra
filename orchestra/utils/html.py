from django.utils.safestring import mark_safe


MONOSPACE_FONTS = ('Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,'
                   'Bitstream Vera Sans Mono,Courier New,monospace')


def monospace_format(text):
    style="font-family:%s;" % MONOSPACE_FONTS
    return mark_safe('<span style="%s">%s</span>' % (style, text))
