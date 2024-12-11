from django import template

register = template.Library()


@register.simple_tag
def get_placeholder(field_name):
    placeholders = {
        "full_name": "First and last name",
        "email": "",
        "password1": "At least 8 characters",
        "password2": "",
    }
    return placeholders.get(field_name, "Enter value")


@register.filter
def does_follow(queryset, obj):
    return queryset.filter(followed_user=obj).exists()
