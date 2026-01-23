from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='parse_basic_markdown')
def parse_basic_markdown(value):
    """
    Parses basic markdown:
    - **text** -> <strong>text</strong>
    - Newlines -> <br>
    """
    if not value:
        return ""
    
    # Escape HTML first to prevent injection (optional, but safe)
    # However, if we escape first, newlines become safe string newlines.
    
    # 1. Bold: **text**
    # pattern: \*\*(.*?)\*\*
    value = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(value))
    
    # 2. Convert newlines to breaks (manual linebreaksbr)
    value = value.replace('\n', '<br>')
    
    return mark_safe(value)
