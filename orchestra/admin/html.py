from django.utils.safestring import mark_safe


MONOSPACE_FONTS = ('Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,'
                   'Bitstream Vera Sans Mono,Courier New,monospace')


def monospace_format(text):
    style="font-family:%s;padding-left:110px;" % MONOSPACE_FONTS
    return mark_safe('<pre style="%s">%s</pre>' % (style, text))
