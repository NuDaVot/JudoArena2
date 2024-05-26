from django import template
from datetime import date

register = template.Library()


@register.filter
def is_ongoing(competition):
    today = date.today()
    return today >= competition.date_event <= competition.date_end


@register.filter
def split_lines(value, line_length):
    words = value.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + len(current_line) > line_length:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word)

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)
