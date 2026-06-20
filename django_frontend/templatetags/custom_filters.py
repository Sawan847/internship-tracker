from django import template

register = template.Library()

@register.filter
def split_skills(value, delimiter=","):
    """Split a comma-separated skills string into a list."""
    if not value:
        return []
    return [s.strip() for s in value.split(delimiter) if s.strip()]
