import asyncio
import time
import os
import ipaddress
import wifi
import socketpool
import adafruit_ntp  # For getting network time (optional but good practice)


# --- Wi-Fi Connection Setup ---
async def connect_wifi():
    print("Attempting to connect to WiFi...")
    while not wifi.radio.ipv4_address:  # Loop until connected
        try:
            wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
            print("Connected to WiFi!")
            print("Pico W IP Address:", wifi.radio.ipv4_address)
            print("Gateway:", wifi.radio.ipv4_gateway)
            print("DNS Server:", wifi.radio.ipv4_dns)
        except Exception as e:
            print(f"Error connecting to WiFi: {e}. Retrying in 5 seconds...")
        await asyncio.sleep(5)  # Use asyncio.sleep for non-blocking delay


# --- UDP Sender Coroutine ---
async def udp_sender(pool, target_host, target_port):
    print(f"UDP Sender Task: Ready to send to {target_host}:{target_port}")
    udp_socket = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)
    message_counter = 0

    while True:
        message_counter += 1
        pico_uptime = time.monotonic()  # Pico's uptime in seconds

        # Get real time if NTP is synced (optional)
        try:
            current_real_time = time.localtime(time.time())  # Requires time.time() to be updated by NTP
            time_str = f"{current_real_time.tm_hour:02}:{current_real_time.tm_min:02}:{current_real_time.tm_sec:02}"
        except AttributeError:
            time_str = "NTP Not Synced"  # Fallback if time.time() isn't working yet

        status_info = f"Pico W Status: Msg #{message_counter}, Uptime: {pico_uptime:.2f}s, Time: {time_str}"

        try:
            # sendto is inherently non-blocking for UDP, even without await in simple case.
            # But in an asyncio context, we call it directly.
            udp_socket.sendto(status_info.encode('utf-8'), (target_host, target_port))
            print(f"UDP Sender Task: Sent: '{status_info}'")
        except OSError as e:
            print(f"UDP Sender Task: Error sending: {e}. (Non-blocking, continuing)")
        except Exception as e:
            print(f"UDP Sender Task: Unexpected error: {e}")

        await asyncio.sleep(2)  # Non-blocking delay for 2 seconds before next send


# --- Other Concurrent Tasks (Examples) ---

async def blink_onboard_led():
    import board
    import digitalio
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT
    print("LED Blinker Task: Starting...")
    while True:
        led.value = True
        await asyncio.sleep(0.5)
        led.value = False
        await asyncio.sleep(0.5)


async def read_sensor_data():
    # Simulate reading a sensor every 3 seconds
    print("Sensor Reader Task: Starting...")
    sensor_value = 0
    while True:
        sensor_value += 1
        print(f"Sensor Reader Task: Reading sensor... Value: {sensor_value}")
        # In a real scenario, you'd read an actual sensor here
        await asyncio.sleep(3)


async def synchronize_time_ntp(pool):
    print("NTP Task: Syncing time...")
    while True:
        try:
            ntp = adafruit_ntp.NTP(pool, tz_offset=0)  # Adjust tz_offset for your timezone (e.g., -4 for Maracaibo)
            # This 'await' makes the network call non-blocking to the event loop
            await ntp.update()
            print(f"NTP Task: Time synced! Current time: {time.localtime()}")
            # It's good to sync less frequently to save power/network traffic
            await asyncio.sleep(3600)  # Sync every hour
        except Exception as e:
            print(f"NTP Task: Error syncing time: {e}. Retrying in 60 seconds...")
            await asyncio.sleep(60)


# --- Main Async Function ---
async def main():
    # First, ensure Wi-Fi connection
    await connect_wifi()

    # Once connected, create the socket pool
    # This must be done AFTER Wi-Fi is connected
    pool = socketpool.SocketPool(wifi.radio)

    # Start the NTP time synchronization task (optional)
    asyncio.create_task(synchronize_time_ntp(pool))

    # Start the UDP sender task
    # Replace with the IP address and port of your computer's UDP server
    TARGET_HOST = 'YOUR_COMPUTER_IP_ADDRESS'  # <<<<< IMPORTANT: e.g., '192.168.1.10'
    TARGET_PORT = 8080
    asyncio.create_task(udp_sender(pool, TARGET_HOST, TARGET_PORT))

    # Start other concurrent tasks
    asyncio.create_task(blink_onboard_led())
    asyncio.create_task(read_sensor_data())

    # Keep the main program running indefinitely (this is required for asyncio)
    while True:
        print("Main Loop: Running in parallel...")
        await asyncio.sleep(10)  # Main loop prints every 10 seconds


# --- Run the asyncio event loop ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        print("Asyncio program exited.")