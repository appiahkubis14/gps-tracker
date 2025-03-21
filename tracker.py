import asyncio
import re
from datetime import datetime

class GPSClient:
    """Manages connected TCP clients and allows sending commands."""
    def __init__(self):
        self.clients = {}

    def add_client(self, imei, writer):
        """Register a new client with IMEI and its writer stream."""
        self.clients[imei] = writer
        print(f"✅ Registered client: {imei}")

    def remove_client(self, imei):
        """Remove disconnected client."""
        if imei in self.clients:
            del self.clients[imei]
            print(f"❌ Client {imei} disconnected")

    async def send_command(self, imei, command):
        """Send a command to the specified IMEI device."""
        if imei in self.clients:
            writer = self.clients[imei]
            writer.write((command + "\r\n").encode())
            await writer.drain()
            print(f"📤 Sent command to {imei}: {command}")
        else:
            print(f"⚠️ Device {imei} not connected")


gps_client_manager = GPSClient()


async def handle_tcp_client(reader, writer):
    """Handle incoming TCP connections from GPS trackers."""
    addr = writer.get_extra_info('peername')
    print(f"📡 TCP Connection from {addr}")

    imei = None  # Store IMEI for disconnection tracking

    try:
        data = await reader.read(1024)
        message = data.decode().strip()
        print(f"📩 Received (TCP): {message}")

        imei, gps_data = parse_gps_message(message)
        if imei:
            gps_client_manager.add_client(imei, writer)
            print_gps_data(imei, gps_data)

        response = "##ACK\r\n"
        writer.write(response.encode())
        await writer.drain()

        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode().strip()
            print(f"📩 Received (TCP): {message}")

    except Exception as e:
        print(f"❌ TCP Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        if imei:
            gps_client_manager.remove_client(imei)


async def handle_udp_client(data, addr):
    """Handle incoming UDP packets from GPS trackers."""
    message = data.decode().strip()
    print(f"📩 Received (UDP) from {addr}: {message}")

    imei, gps_data = parse_gps_message(message)
    if imei:
        print_gps_data(imei, gps_data)


async def start_udp_server():
    """Start the UDP server."""
    loop = asyncio.get_running_loop()
    udp_server = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(),
        local_addr=('192.168.100.251', 10110)
    )
    print("🚀 GPS Server Running (UDP:10110)")
    await udp_server[1]


class UDPServerProtocol:
    """Handle UDP connections for GPS trackers."""

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.create_task(handle_udp_client(data, addr))


def parse_gps_message(message):
    """Extract IMEI and GPS data fields from incoming messages."""
    match = re.match(
        r"\$\$(\d+),(\d+),(.+),A00,(.+),(.+),([AV]),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+),(.+)",
        message
    )
    if match:
        imei = match.group(2)
        gps_data = {
            'timestamp': datetime.strptime(match.group(6), '%y%m%d%H%M%S'),
            'fix_flag': match.group(7),
            'latitude': float(match.group(8)),
            'longitude': float(match.group(9)),
            'speed': float(match.group(10)),
            'course': float(match.group(11)),
        }
        return imei, gps_data
    return None, None


def print_gps_data(imei, gps_data):
    """Print GPS data to console."""
    print(f"\n📍 GPS Data from {imei}:")
    print(f"   📌 Latitude: {gps_data['latitude']}, Longitude: {gps_data['longitude']}")
    print(f"   🚗 Speed: {gps_data['speed']} km/h")
    print(f"   📅 Time: {gps_data['timestamp']}")
    print("--------------------------------------------------")


async def start_servers():
    """Start TCP & UDP servers for GPS tracking."""
    tcp_server = await asyncio.start_server(handle_tcp_client, '192.168.100.251', 10100)
    print("🚀 GPS Server Running (TCP:10100)")

    udp_task = asyncio.create_task(start_udp_server())

    # Start a separate task for handling user commands
    command_task = asyncio.create_task(command_input())

    async with tcp_server:
        await asyncio.gather(tcp_server.serve_forever(), udp_task, command_task)


async def command_input():
    """Allow user to send commands to connected GPS devices."""
    while True:
        imei = input("\nEnter IMEI to send command (or 'exit' to quit): ").strip()
        if imei.lower() == "exit":
            break
        command = input("Enter command to send: ").strip()
        await gps_client_manager.send_command(imei, command)


if __name__ == "__main__":
    asyncio.run(start_servers())
