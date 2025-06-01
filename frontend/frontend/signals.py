from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Subscription


@receiver(post_save, sender=User)
def create_default_subscription(sender, instance, created, **kwargs):
    if created:
        Subscription.objects.create(
            user=instance,
            plan=getattr(settings, 'DEFAULT_PLAN', 'basic'),
            status='active',
            start_date=timezone.now().date(),
        )
