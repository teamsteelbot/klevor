from time import sleep
from os import getenv
from ipaddress import ip_address
from wifi import radio
from socketpool import SocketPool

class WifiError(Exception):
    """
    Custom exception for Wi-Fi errors.
    """
    def __init__(self, message):
        """
        Initializes the WifiError with a custom message.
        """
        super().__init__(message)
        self.message = message

    def __str__(self):
        """
        Returns a string representation of the WifiError.
        """
        return f"Wi-Fi Error: {self.message}"

class WifiHandler:
    """
    A class to handle Wi-Fi connection and UDP socket operations.
    """
    # Default configuration
    ATTEMPTS = 5
    ATTEMPT_DELAY = 5
    SSID = getenv("WIFI_SSID", "default_ssid")
    PASSWORD = getenv("WIFI_PASSWORD", "default_password")
    TARGET_IP = getenv("SOCKET_SERVER_IP", "default_target_ip")
    TARGET_PORT = int(getenv("SOCKET_SERVER_PORT", 12345))

    def __init__(self, ssid: str = SSID, password: str = PASSWORD):
        """
        Initializes the WifiHandler with default values.
        """
        # Set the Wi-Fi credentials
        self.__ssid = ssid
        self.__password = password

        # Initialize attributes
        self.__pool = None
        self.__udp_socket = None
        self.__ipv4_address = None
        self.__ipv4_gateway = None
        self.__ipv4_dns = None

    async def connect(self, attempts: int = ATTEMPTS):
        """
        Connect to WI-FI using credentials from environment variables.
        """
        # Initialize Wi-Fi status
        counter = 0
        while not self.__ipv4_address and counter < attempts:
            try:
                radio.connect(self.__ssid, self.__password)
                self.__ipv4_address = radio.ipv4_address
                self.__ipv4_gateway = radio.ipv4_gateway
                self.__ipv4_dns =  radio.ipv4_dns

            except Exception:
                pass

            sleep(self.ATTEMPT_DELAY)
            counter += 1

        if not self.__ipv4_address:
            raise WifiError("Failed to connect to Wi-Fi after multiple attempts.")

    def create_socket(self):
        """
        Create a socket pool for creating sockets.
        """
        if not self.__ipv4_address:
            raise WifiError("Wi-Fi is not connected. Cannot create socket pool.")

        try:
            self.__pool = SocketPool(radio)

        except Exception as e:
            raise WifiError(f"Error creating socket pool: {e}")

    def create_udp_socket(self):
        """
        Create UDP socket.
        """
        if not self.__pool:
            raise WifiError("Socket pool is not available. Cannot create UDP socket.")

        try:
            self.__udp_socket = self.__pool.socket(self.__pool.AF_INET, self.__pool.SOCK_DGRAM)
            self.__udp_socket.setblocking(False)

        except Exception as e:
            raise WifiError(f"Error creating UDP socket: {e}")

    def close_udp_socket(self):
        """
        Close UDP socket.
        """
        if not self.__udp_socket:
            raise WifiError("UDP socket is not available. Cannot close UDP socket.")

        try:
            self.__udp_socket.close()

        except Exception as e:
            print(f"Error closing UDP socket: {e}")

    async def send_udp_message(self, message: str, target_ip: str = TARGET_IP, target_port: int = TARGET_PORT):
        """
        Send message over UDP

        Args:
            message (str): The message to send.
            target_ip (str): The target IP address.
            target_port (int): The target port number.
        """
        if not self.__udp_socket:
            raise WifiError("UDP socket is not created. Cannot send message.")

        # Validate target ip and port
        if not target_ip or not target_port:
            raise WifiError("Target host or port is not set. Cannot send message.")
        ip_address(target_ip)

        try:
            self.__udp_socket.sendto(message.encode('utf-8'), (target_ip, target_port))

        except OSError as e:
            print(f"Error sending message: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")

    def __del__(self):
        """
        Destructor to close the WI-FI connection and clean up resources.
        """
        if self.__udp_socket:
            self.close_udp_socket()

        if self.__pool:
            del self.__pool

        if self.__ipv4_address:
            radio.disconnect()