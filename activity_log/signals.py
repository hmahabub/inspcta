from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ActivityLog

User = get_user_model()

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender.__name__ not in ['ActivityLog', 'LogEntry']:  # Avoid logging logs
        action = "Created" if created else "Updated"
        user = None
        if hasattr(instance, 'request'):
            user = instance.request.user
        ActivityLog.objects.create(
            user=user,
            action=f"{action} {sender.__name__}",
            model=sender.__name__,
            object_id=instance.pk
        )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender.__name__ not in ['ActivityLog', 'LogEntry']:
        user = None
        if hasattr(instance, 'request'):
            user = instance.request.user
        ActivityLog.objects.create(
            user=user,
            action=f"Deleted {sender.__name__}",
            model=sender.__name__,
            object_id=instance.pk
        )