from django.utils.safestring import mark_safe


MONOSPACE_FONTS = ('Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,'
                   'Bitstream Vera Sans Mono,Courier New,monospace')


def monospace_format(text):
    style="font-family:%s;padding-left:110px;white-space:pre-wrap;" % MONOSPACE_FONTS
    return mark_safe('<pre style="%s">%s</pre>' % (style, text))


def code_format(text, language='bash'):
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    lexer = get_lexer_by_name(language, stripall=True)
    formatter = HtmlFormatter(linenos=True)
    code = highlight(text, lexer, formatter)
    return mark_safe('<div style="padding-left:110px;">%s</div>' % code)
