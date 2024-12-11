from django import template

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name="dates_different")
def dates_different(created_at, updated_at):
    return created_at != updated_at


@register.filter(name="add_float")
def add_float(value, arg):
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return ""
