from django import template
from courses.cart import Cart

register = template.Library()


@register.simple_tag(takes_context=True)
def get_cart_count(context, request=None):
    if request is None:
        request = context.get('request')
    if request is None:
        return 0
    cart = Cart(request)
    return len(cart)
