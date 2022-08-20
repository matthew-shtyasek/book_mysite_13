from django import template

register = template.Library()


@register.filter
def change_lang(request, lang):
    request.LANGUAGE_CODE = lang
    url = request.path.split('/', maxsplit=2)[2]
    return f'/{lang}/{url}'
