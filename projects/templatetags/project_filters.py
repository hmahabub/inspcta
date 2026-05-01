from django import template

register = template.Library()

@register.filter(name='sum_attribute')
def sum_attribute(queryset, attribute):
    """Sum a specific attribute across a queryset"""
    total = 0
    if queryset:
        for obj in queryset:
            total += float(getattr(obj, attribute, 0))
    return total

@register.filter(name='add')
def add(value, arg):
    """Add two values"""
    try:
        return float(value) + float(arg)
    except (TypeError, ValueError):
        return 0

@register.filter(name='sub')
def sub(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (TypeError, ValueError):
        return 0

@register.filter(name='div')
def div(value, arg):
    """Divide value by arg"""
    try:
        if arg and float(arg) != 0:
            return float(value) / float(arg)
        return 0
    except (TypeError, ValueError, ZeroDivisionError):
        return 0

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0