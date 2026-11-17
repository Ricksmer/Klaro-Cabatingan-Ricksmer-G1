from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        EDITOR = 'editor', 'Editor'
        CITIZEN = 'citizen', 'Citizen'

    email = models.EmailField('email address', unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CITIZEN)
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^[0-9+\-\s()]{7,20}$', 'Enter a valid contact number.')],
    )
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Superusers created with createsuperuser are always Admins
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def get_dashboard_url(self):
        names = {
            self.Role.ADMIN: 'accounts:admin_dashboard',
            self.Role.EDITOR: 'accounts:editor_dashboard',
            self.Role.CITIZEN: 'accounts:citizen_dashboard',
        }
        return reverse(names[self.role])

    def __str__(self):
        return self.username