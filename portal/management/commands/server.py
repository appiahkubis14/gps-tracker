import asyncio
import re
import django
from django.conf import settings
from datetime import datetime

# Set up Django environment
django.setup()
from portal.models import GPSDevice, GPSData, GPSCommand

async def handle_tcp_client(reader, writer):
    """Handles incoming TCP data and sends pending commands."""
    addr = writer.get_extra_info('peername')
    print(f"📡 TCP Connection from {addr}")

    data = await reader.read(1024)
    message = data.decode().strip()
    print(f"📩 Received (TCP): {message}")

    imei, gps_data = parse_gps_message(message)
    if imei:
        store_gps_data(imei, gps_data)

        # Retrieve and send pending commands
        device = GPSDevice.objects.filter(imei=imei).first()
        if device:
            pending_commands = GPSCommand.objects.filter(device=device, status="Pending")
            for cmd in pending_commands:
                print(f"📤 Sending Command: {cmd.command}")
                writer.write((cmd.command + "\r\n").encode())
                await writer.drain()
                cmd.status = "Sent"
                cmd.save()

    response = "##ACK\r\n"
    writer.write(response.encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

def parse_gps_message(message):
    """Extract IMEI and GPS data from incoming message."""
    match = re.match(r"\$\$(\d+),(\d+),(.+),A00,(.+),(.+),([AV]),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+)", message)
    if match:
        imei = match.group(2)
        gps_data = {
            'timestamp': datetime.strptime(match.group(5), '%y%m%d%H%M%S'),
            'latitude': float(match.group(7)),
            'longitude': float(match.group(8)),
            'speed': float(match.group(9)),
            'altitude': float(match.group(11)),
            'status': match.group(16),
        }
        return imei, gps_data
    return None, None

def store_gps_data(imei, gps_data):
    """Store GPS data in PostgreSQL."""
    try:
        device, created = GPSDevice.objects.get_or_create(imei=imei)
        GPSData.objects.create(
            device=device,
            timestamp=gps_data['timestamp'],
            latitude=gps_data['latitude'],
            longitude=gps_data['longitude'],
            speed=gps_data['speed'],
            altitude=gps_data['altitude'],
            status=gps_data['status']
        )
        print(f"✅ Data stored for {imei}")
    except Exception as e:
        print(f"❌ Database Error: {e}")

async def start_servers():
    """Start TCP server."""
    server = await asyncio.start_server(handle_tcp_client, '194.135.89.211 ', 10502)
    async with server:
        print("🚀 GPS Server Running (TCP:5000)")
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(start_servers())
