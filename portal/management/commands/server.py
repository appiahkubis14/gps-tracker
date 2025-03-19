import socketserver
import threading
from django.core.management.base import BaseCommand
from portal.tracker_server import TCPHandler, UDPHandler


class Command(BaseCommand):
    help = "Starts the tracker server (TCP & UDP)."

    def handle(self, *args, **options):
        TCP_HOST, TCP_PORT = "192.168.100.251", 5000  # TCP Server
        UDP_HOST, UDP_PORT = "192.168.100.251", 5001  # UDP Server

        # Create the TCP and UDP servers
        tcp_server = socketserver.ThreadingTCPServer((TCP_HOST, TCP_PORT), TCPHandler)
        udp_server = socketserver.ThreadingUDPServer((UDP_HOST, UDP_PORT), UDPHandler)

        print(f"Starting TCP Server on {TCP_HOST}:{TCP_PORT}")
        print(f"Starting UDP Server on {UDP_HOST}:{UDP_PORT}")

        # Run servers in separate threads
        tcp_thread = threading.Thread(target=tcp_server.serve_forever)
        udp_thread = threading.Thread(target=udp_server.serve_forever)

        tcp_thread.daemon = True
        udp_thread.daemon = True

        tcp_thread.start()
        udp_thread.start()

        print("Tracker Server is running...")
        tcp_thread.join()
        udp_thread.join()
