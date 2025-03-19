import socketserver
import threading
import json
from datetime import datetime
from django.utils.timezone import now
from django.core.management.base import BaseCommand
from portal.models import TrackerData


# ----------------------------
# TCP Server Handler
# ----------------------------
class TCPHandler(socketserver.BaseRequestHandler):
    """Handles incoming TCP tracker data."""
    
    def handle(self):
        try:
            data = self.request.recv(1024).strip().decode("utf-8")
            print(f"Received TCP Data: {data}")

            # Parse received data (assuming JSON format)
            data_dict = json.loads(data)
            imei = data_dict.get("imei")
            lat = float(data_dict.get("lat", 0))
            lng = float(data_dict.get("lng", 0))
            speed = float(data_dict.get("speed", 0))
            dt_tracker = datetime.strptime(data_dict.get("dt", now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")

            # Save to database
            TrackerData.objects.create(
                imei=imei,
                protocol="tcp",
                ip=self.client_address[0],
                port=self.client_address[1],
                dt_server=now(),
                dt_tracker=dt_tracker,
                lat=lat,
                lng=lng,
                speed=speed,
                loc_valid=True,
                params=data_dict
            )

            self.request.sendall(b"ACK\n")  # Acknowledge receipt

        except Exception as e:
            print(f"Error in TCPHandler: {e}")


# ----------------------------
# UDP Server Handler
# ----------------------------
class UDPHandler(socketserver.BaseRequestHandler):
    """Handles incoming UDP tracker data."""
    
    def handle(self):
        try:
            data, socket = self.request
            message = data.strip().decode("utf-8")
            print(f"Received UDP Data: {message}")

            # Parse received data (assuming JSON format)
            data_dict = json.loads(message)
            imei = data_dict.get("imei")
            lat = float(data_dict.get("lat", 0))
            lng = float(data_dict.get("lng", 0))
            speed = float(data_dict.get("speed", 0))
            dt_tracker = datetime.strptime(data_dict.get("dt", now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")

            # Save to database
            TrackerData.objects.create(
                imei=imei,
                protocol="udp",
                ip=self.client_address[0],
                port=self.client_address[1],
                dt_server=now(),
                dt_tracker=dt_tracker,
                lat=lat,
                lng=lng,
                speed=speed,
                loc_valid=True,
                params=data_dict
            )

            socket.sendto(b"ACK\n", self.client_address)  # Acknowledge receipt

        except Exception as e:
            print(f"Error in UDPHandler: {e}")
