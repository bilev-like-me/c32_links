from celery import shared_task
from django_celery_beat.models import PeriodicTask
from django.utils import timezone
from datetime import timedelta

from .models import ShortLinks


@shared_task(name="delete_old_links")
def delete_old_links(weeks=0, days=0, hours=0, minutes=0):
    ShortLinks.objects.filter(
        date_time__lte=(
            timezone.now() - timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes)
            )
        ).delete()

