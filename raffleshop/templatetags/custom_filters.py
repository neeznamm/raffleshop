from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.filter(name='remaining_time')
def remaining_time(end_datetime):
    now = timezone.now()
    time_difference = end_datetime - now
    is_future = time_difference.total_seconds() > 0

    time_difference = abs(time_difference)
    weeks = time_difference.days // 7
    days = time_difference.days % 7
    months = weeks // 4
    weeks %= 4

    parts = []
    if months > 0:
        parts.append(f"{months}M")
    if weeks > 0:
        parts.append(f"{weeks}W")
    if days > 0 or (months == 0 and weeks == 0):
        parts.append(f"{days}D")

    formatted_time = " ".join(parts)
    return (formatted_time, is_future)
