from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter(name='dates_different')
def dates_different(created_at, updated_at):
    return created_at != updated_at