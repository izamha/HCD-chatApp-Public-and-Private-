import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _
from PIL import Image
from django.urls import reverse


class UserManager(BaseUserManager):
    """Define a model manager for a custom user"""

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email should be provided.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    name = models.CharField(verbose_name="Name", max_length=255, blank=False, null=True)
    email = models.EmailField(max_length=254, blank=False, null=True, unique=True,
                              error_messages={'required': _('Your email please!'),
                                              'unique': _('There is someone else using this email.')})
    password = models.CharField(verbose_name=_('Password'), max_length=150, null=False)
    public_id = models.UUIDField(unique=True, primary_key=False, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return '%s' % self.email

    def get_absolute_url(self):
        return reverse('room', args=[self.public_id])

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profiles', null=True)

    def __str__(self):
        return f"Profile ya {self.user.name}"

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    """Decrease the image size before save()"""

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
