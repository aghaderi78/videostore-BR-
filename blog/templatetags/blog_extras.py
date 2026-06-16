from django import template
from courses.models import Course

register = template.Library()


@register.simple_tag
def featured_courses():
    return Course.objects.filter(is_active=True).order_by('-published_at')[:4]
