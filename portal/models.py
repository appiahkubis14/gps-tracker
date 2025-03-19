from django.db import models
from django.contrib.auth.models import AbstractUser


class GSUser(AbstractUser):
    """User model with API Key for authentication."""
    api_key = models.CharField(max_length=255, unique=True)
    api = models.BooleanField(default=False)  # Matches PHP 'true'/'false'

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="gsuser_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="gsuser_permissions_set",
        blank=True
    )

    def __str__(self):
        return self.username

    @staticmethod
    def get_user_id_from_api_key(api_key):
        """Retrieve user ID from API key."""
        user = GSUser.objects.filter(api_key=api_key, api=True).first()
        return user.id if user else None


class TrackerData(models.Model):
    """Stores tracker data received via API."""
    imei = models.CharField(max_length=50)
    protocol = models.CharField(max_length=20, default="api_loc")
    ip = models.GenericIPAddressField(null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    dt_server = models.DateTimeField(auto_now_add=True)  # Default to current UTC time
    dt_tracker = models.DateTimeField()
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    angle = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    loc_valid = models.BooleanField(default=False)
    params = models.JSONField(default=dict)  # Store additional parameters as JSON
    event = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Tracker {self.imei} - {self.dt_tracker}"


class AddUser(models.Model):
    """Represents a user with additional privileges."""
    email = models.EmailField(unique=True)
    privileges = models.JSONField(default=dict)

    def __str__(self):
        return self.email


# class AddObject(models.Model):
#     """Represents an object added to the tracking system."""
#     imei = models.CharField(max_length=50, unique=True)
#     name = models.CharField(max_length=100)
#     active = models.BooleanField(default=False)
#     active_dt = models.DateTimeField()

#     def __str__(self):
#         return self.name

class AddObject(models.Model):
    """Stores objects (devices) with tracking capabilities."""
    imei = models.CharField(max_length=20, unique=True)
    protocol = models.CharField(max_length=20)
    ip = models.GenericIPAddressField(null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=False)
    active_dt = models.DateTimeField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.imei})"



class AddUserObject(models.Model):
    """Many-to-Many relationship between users and objects."""
    user = models.ForeignKey(AddUser, on_delete=models.CASCADE)
    object = models.ForeignKey(AddObject, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} - {self.object.imei}"


class UserObject(models.Model):
    """Many-to-Many relationship between GSUser and Objects."""
    user = models.ForeignKey(GSUser, on_delete=models.CASCADE)
    object = models.ForeignKey(AddObject, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.object.imei}"


class Command(models.Model):
    """Handles commands sent to objects (devices)."""
    imei = models.ForeignKey(AddObject, on_delete=models.CASCADE)
    user = models.ForeignKey(GSUser, on_delete=models.CASCADE)
    cmd = models.TextField()
    status = models.BooleanField(default=False)  # Equivalent to PHP true/false

    def __str__(self):
        return f"Command {self.imei.imei} by {self.user.username} - {self.status}"


class ObjectActivity(models.Model):
    """Tracks activation/deactivation of objects."""
    imei = models.ForeignKey(AddObject, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    active_dt = models.DateTimeField()

    def __str__(self):
        return f"{self.imei.imei} - {'Active' if self.active else 'Inactive'}"


class APICommand(models.Model):
    """Handles API-based commands and responses."""
    command = models.CharField(max_length=50)
    params = models.JSONField(default=dict)
    user = models.ForeignKey(GSUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"API Command: {self.command} - {self.created_at}"
