from django.db import models

class GPSDevice(models.Model):
    imei = models.CharField(max_length=20, unique=True)
    device_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.device_name} ({self.imei})"

from django.db import models

class GPSData(models.Model):
    terminal_id = models.CharField(max_length=20, unique=True)  # ID
    work_no = models.CharField(max_length=10)  # Work number (hex)
    alarm_code = models.CharField(max_length=50, blank=True, null=True)  # Alarm Code | Alarm Parameter
    date_time = models.DateTimeField()  # UTC timestamp
    fix_flag = models.CharField(max_length=1)  # GPS status flag (A/V)
    latitude = models.FloatField()  # Latitude
    longitude = models.FloatField()  # Longitude
    speed = models.FloatField()  # Speed (km/h)
    course = models.FloatField()  # Running direction (degrees)
    altitude = models.FloatField()  # Altitude (meters)
    odometer = models.FloatField()  # Odometer (meters)
    fuel_consume = models.FloatField(blank=True, null=True)  # Fuel consumption
    status = models.CharField(max_length=10)  # Status flags (hex)
    input_status = models.CharField(max_length=10, blank=True, null=True)  # Input state (hex)
    output_status = models.CharField(max_length=10, blank=True, null=True)  # Output state (hex)
    mcc = models.CharField(max_length=10, blank=True, null=True)  # Mobile Country Code
    mnc = models.CharField(max_length=10, blank=True, null=True)  # Mobile Network Code
    lac = models.CharField(max_length=10, blank=True, null=True)  # Location Area Code
    ci = models.CharField(max_length=10, blank=True, null=True)  # Cell ID
    battery_voltage = models.CharField(max_length=20, blank=True, null=True)  # Battery voltage and other sensor data

    def __str__(self):
        return f"GPS Data {self.terminal_id} @ {self.date_time}"


class GPSCommand(models.Model):
    device = models.ForeignKey(GPSDevice, on_delete=models.CASCADE)
    command = models.TextField()
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Sent", "Sent"), ("Acknowledged", "Acknowledged")], default="Pending")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.imei} - {self.command} ({self.status})"
