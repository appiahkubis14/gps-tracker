from django.db import models

class GPSDevice(models.Model):
    imei = models.CharField(max_length=20, unique=True)
    device_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.device_name} ({self.imei})"

class GPSData(models.Model):
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed = models.FloatField(default=0)
    altitude = models.FloatField(default=0)
    status = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.device.imei} - {self.timestamp}"

class GPSCommand(models.Model):
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE)
    command = models.TextField()
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Sent", "Sent"), ("Acknowledged", "Acknowledged")], default="Pending")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.imei} - {self.command} ({self.status})"
