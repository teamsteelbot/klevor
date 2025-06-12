from argparse import ArgumentParser
import pygame
import math
import asyncio
from threading import Thread
from websockets import connect

from args import Args
from server import RealtimeTrackerServer
from rplidar import RPLIDAR
from rplidar.measure import Measure

class App:
    """
    Klevor RPLIDAR GUI Application.
    """
    # IP and port for the WebSocket server
    IP = "0.0.0.0"
    PORT = 8765

    # Application size and scaling factors
    APP_SIZE = 800
    MAX_DISTANCE_RADIUS = RPLIDAR.MAX_DISTANCE_LIMIT
    MAX_DISTANCE_RADIUS_FACTOR = APP_SIZE / (2 * MAX_DISTANCE_RADIUS)
    RADIUS = APP_SIZE // 2
    CENTER_X = APP_SIZE // 2
    CENTER_Y = APP_SIZE // 2
    BACKGROUND_COLOR = (255, 255, 255)

    # Point properties
    POINT_RADIUS = 3
    POINT_COLOR = (255, 0, 0)  # Red
    POINT_BORDER_COLOR = (0, 0, 0)  # Black
    POINT_BORDER_WIDTH = 1

    # Central point properties
    CENTRAL_POINT_RADIUS = 5
    CENTRAL_POINT_COLOR = (0, 0, 255)  # Blue

    # Static circle properties
    STATIC_CIRCLE_RADIUS = 1000
    INTERNAL_STATIC_CIRCLE_COLOR = (0, 0, 0)  # Black
    INTERNAL_STATIC_CIRCLE_WIDTH = 2
    EXTERNAL_STATIC_CIRCLE_COLOR = (0, 0, 0)  # Black
    EXTERNAL_STATIC_CIRCLE_WIDTH = 3

    # Update properties
    UPDATE_DELAY = 50  # ms
    DISTANCE_MINIMUM_DIFFERENCE = 50
    
    def __init__(self, ip: str, port: int):
        """
        Initializes the application with the given IP and port.
        
        Args:
            ip (str): The IP address of the WebSocket server.
            port (int): The port of the WebSocket server.
        """
        # Initialize the GUI
        pygame.init()
        self.__screen = pygame.display.set_mode((self.APP_SIZE, self.APP_SIZE))
        pygame.display.set_caption("Klevor RPLIDAR GUI")
        self.__clock = pygame.time.Clock()
        self.__running = True

        # Initialize the measures and points-related objects
        self.__measures = []
        self.__previous_measures = {}
        self.__point_positions = {}
        
        # Initialize the WebSocket server connection parameters
        self.__ip = ip
        self.__port = port
        self.__url = f'ws://{self.__ip}:{self.__port}'

    def draw_static(self):
        """
        Draws the static elements of the GUI, including circles and central point.
        """
        # Draw static circles
        n = int(self.MAX_DISTANCE_RADIUS / self.STATIC_CIRCLE_RADIUS)
        is_exact = self.MAX_DISTANCE_RADIUS % self.STATIC_CIRCLE_RADIUS == 0
        for i in range(1, n+1):
            radius = i * self.STATIC_CIRCLE_RADIUS * self.MAX_DISTANCE_RADIUS_FACTOR
            color = self.INTERNAL_STATIC_CIRCLE_COLOR if not is_exact or i < n else self.EXTERNAL_STATIC_CIRCLE_COLOR
            width = self.INTERNAL_STATIC_CIRCLE_WIDTH if not is_exact or i < n else self.EXTERNAL_STATIC_CIRCLE_WIDTH
            pygame.draw.circle(self.__screen, color, (self.CENTER_X, self.CENTER_Y), radius, width)

        # Draw external static circle
        if not is_exact:
            pygame.draw.circle(self.__screen, self.EXTERNAL_STATIC_CIRCLE_COLOR, (self.CENTER_X, self.CENTER_Y), self.RADIUS, self.EXTERNAL_STATIC_CIRCLE_WIDTH)

        # Draw central point
        pygame.draw.circle(self.__screen, self.CENTRAL_POINT_COLOR, (self.CENTER_X, self.CENTER_Y), self.CENTRAL_POINT_RADIUS)

    def update_points(self):
        """
        Updates the positions of the points based on the current measures.
        This method calculates the positions of the points based on the angle and distance
        of each measure, and stores them in the __point_positions dictionary.
        """
        for measure in self.__measures:
            prev = self.__previous_measures.get(measure.angle)
            if prev and abs(prev.distance - measure.distance) < self.DISTANCE_MINIMUM_DIFFERENCE:
                continue
            self.__previous_measures[measure.angle] = measure

            radian_angle = math.radians(measure.angle)
            x = int(self.CENTER_X + measure.distance * math.cos(radian_angle) * self.MAX_DISTANCE_RADIUS_FACTOR)
            y = int(self.CENTER_Y + measure.distance * math.sin(radian_angle) * self.MAX_DISTANCE_RADIUS_FACTOR)
            self.__point_positions[measure.angle] = (x, y)

        """
        # Optionally, remove old points
        current_angles = set(m.angle for m in self.__measures)
        for angle in list(self.__point_positions):
            if angle not in current_angles:
                del self.__point_positions[angle]
        """

    def draw_points(self):
        """
        Draws the points on the __screen based on the current measures.
        """
        for pos in self.__point_positions.values():
            # Draw the point
            pygame.draw.circle(self.__screen, self.POINT_COLOR, pos, self.POINT_RADIUS)

            # Draw border around the point
            pygame.draw.circle(self.__screen, self.POINT_BORDER_COLOR, pos, self.POINT_RADIUS, self.POINT_BORDER_WIDTH)

    def run(self):
        """
        Main loop of the application that handles events, updates the display, and draws the GUI.
        This method runs until the application is closed.
        """
        while self.__running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__running = False

            self.__screen.fill(self.BACKGROUND_COLOR)
            self.draw_static()
            self.update_points()
            self.draw_points()
            pygame.display.flip()
            self.__clock.tick(1000 // self.UPDATE_DELAY)

        pygame.quit()

    async def ws_listener(self):
        """
        Asynchronously listens for messages from the WebSocket server and updates the measures.
        This method connects to the WebSocket server and processes incoming messages,
        updating the measures accordingly.
        """

        print(f"Connecting to WebSocket server at {self.__url}...")
        async with connect(self.__url) as ws:
            while True:
                msg = await ws.recv()
                parts = msg.split(RealtimeTrackerServer.TAG_SEPARATOR)
                if parts[0] == RealtimeTrackerServer.TAG_RPLIDAR_MEASURES:
                    self.__measures = Measure.from_string_to_measures(parts[1])

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Script to run the Klevor RPLIDAR GUI application.",
    )
    Args.add_ip_argument(parser, default=App.IP)
    Args.add_port_argument(parser, default=App.PORT)
    args = Args.parse_args_as_dict(parser)

    # Get the IP address from the arguments
    ip = Args.get_attribute_from_args(args, Args.IP)
    
    # Get the port from the arguments
    port = Args.get_attribute_from_args(args, Args.PORT)

    app = App(ip, port)
    ws_thread = Thread(target=asyncio.run, args=(app.ws_listener(),), daemon=True)
    ws_thread.start()
    app.run()