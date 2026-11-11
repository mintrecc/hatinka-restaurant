from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Extra guest data. Linked to the standard User model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='User',
        on_delete=models.CASCADE,
        related_name='profile',
    )
    phone = models.CharField('Phone', max_length=20, blank=True)
    default_address = models.CharField('Default delivery address', max_length=255, blank=True)
    birth_date = models.DateField('Birth date', null=True, blank=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f'Profile of {self.user}'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    """Automatically create a profile when a user is registered."""
    if created:
        Profile.objects.create(user=instance)