from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model with additional fields"""
    email = models.EmailField(_('email address'), unique=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    """Extended user profile with additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_('bio'), blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True)
    preferences = models.JSONField(_('preferences'), default=dict)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return f"{self.user.email}'s profile"

class UserRole(models.Model):
    """Role model for role-based access control"""
    name = models.CharField(_('name'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True)
    permissions = models.JSONField(_('permissions'), default=list)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('user role')
        verbose_name_plural = _('user roles')
        ordering = ['name']

    def __str__(self):
        return self.name

class UserRoleAssignment(models.Model):
    """Model for assigning roles to users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE, related_name='user_assignments')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='role_assignments_created')

    class Meta:
        verbose_name = _('user role assignment')
        verbose_name_plural = _('user role assignments')
        unique_together = ['user', 'role']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.role.name}" 