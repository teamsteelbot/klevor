import socket
import time

from .constants import HOST, PORT

# UDP Server Setup
print("Starting UDP Server...")
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set the socket to non-blocking mode for receive operations
udp_server_socket.setblocking(False)

try:
    udp_server_socket.bind((HOST, PORT))
    print(f"Computer UDP Server listening on {HOST}:{PORT}")

    while True:
        try:
            # Try to receive data. This will raise BlockingIOError if no data.
            data, addr = udp_server_socket.recvfrom(1024)
            message = data.decode('utf-8').strip()
            print(f"[UDP Server - {addr}] Received: {message}")

        except BlockingIOError:
            # No data received in this iteration, which is expected in non-blocking mode.
            pass

        except Exception as e:
            print(f"[UDP Server] Error receiving UDP data: {e}")

        time.sleep(0.5) # Small delay to avoid busy-waiting, but still responsive

except KeyboardInterrupt:
    print("\nServer stopped by user (Ctrl+C).")

except Exception as e:
    print(f"An error occurred in the main server loop: {e}")

finally:
    if 'udp_server_socket' in locals() and udp_server_socket:
        udp_server_socket.close()
        print("UDP server socket closed.")

    print("Program exited.")