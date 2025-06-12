import pygame
import math
import asyncio
from threading import Thread
from websockets import connect

from server import RealtimeTrackerServer
from rplidar import RPLIDAR
from rplidar.measure import Measure

# IP and port for the WebSocket server
IP = "0.0.0.0"
PORT = 8765

# Application size and scaling factors
APP_SIZE = 800
MAX_DISTANCE_RADIUS = RPLIDAR.MAX_DISTANCE_LIMIT
MAX_DISTANCE_RADIUS_FACTOR = APP_SIZE / (2*MAX_DISTANCE_RADIUS)
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

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((APP_SIZE, APP_SIZE))
        pygame.display.set_caption("Klevor RPLIDAR GUI")
        self.clock = pygame.time.Clock()
        self.running = True

        self.measures = []
        self.previous_measures = {}
        self.point_positions = {}

    def draw_static(self):
        """
        Draws the static elements of the GUI, including circles and central point.
        """
        # Draw static circles
        n = int(MAX_DISTANCE_RADIUS / STATIC_CIRCLE_RADIUS)
        is_exact = MAX_DISTANCE_RADIUS % STATIC_CIRCLE_RADIUS == 0
        for i in range(1, n+1):
            radius = i * STATIC_CIRCLE_RADIUS * MAX_DISTANCE_RADIUS_FACTOR
            color = INTERNAL_STATIC_CIRCLE_COLOR if not is_exact or i < n else EXTERNAL_STATIC_CIRCLE_COLOR
            width = INTERNAL_STATIC_CIRCLE_WIDTH if not is_exact or i < n else EXTERNAL_STATIC_CIRCLE_WIDTH
            pygame.draw.circle(self.screen, color, (CENTER_X, CENTER_Y), radius, width)
            print(f"Drawing circle {i} with radius {radius}, color {color}, width {width}")

        # Draw external static circle
        if not is_exact:
            pygame.draw.circle(self.screen, EXTERNAL_STATIC_CIRCLE_COLOR, (CENTER_X, CENTER_Y), RADIUS, EXTERNAL_STATIC_CIRCLE_WIDTH)

        # Draw central point
        pygame.draw.circle(self.screen, CENTRAL_POINT_COLOR, (CENTER_X, CENTER_Y), CENTRAL_POINT_RADIUS)

    def update_points(self):
        """
        Updates the positions of the points based on the current measures.
        This method calculates the positions of the points based on the angle and distance
        of each measure, and stores them in the point_positions dictionary.
        """
        for measure in self.measures:
            prev = self.previous_measures.get(measure.angle)
            if prev and abs(prev.distance - measure.distance) < DISTANCE_MINIMUM_DIFFERENCE:
                continue
            self.previous_measures[measure.angle] = measure

            radian_angle = math.radians(measure.angle)
            x = int(CENTER_X + measure.distance * math.cos(radian_angle) * MAX_DISTANCE_RADIUS_FACTOR)
            y = int(CENTER_Y + measure.distance * math.sin(radian_angle) * MAX_DISTANCE_RADIUS_FACTOR)
            self.point_positions[measure.angle] = (x, y)

        """
        # Optionally, remove old points
        current_angles = set(m.angle for m in self.measures)
        for angle in list(self.point_positions):
            if angle not in current_angles:
                del self.point_positions[angle]
        """

    def draw_points(self):
        """
        Draws the points on the screen based on the current measures.
        """
        for pos in self.point_positions.values():
            # Draw the point
            pygame.draw.circle(self.screen, POINT_COLOR, pos, POINT_RADIUS)

            # Draw border around the point
            pygame.draw.circle(self.screen, POINT_BORDER_COLOR, pos, POINT_RADIUS, POINT_BORDER_WIDTH)

    def run(self):
        """
        Main loop of the application that handles events, updates the display, and draws the GUI.
        This method runs until the application is closed.
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill(BACKGROUND_COLOR)
            self.draw_static()
            self.update_points()
            self.draw_points()
            pygame.display.flip()
            self.clock.tick(1000 // UPDATE_DELAY)

        pygame.quit()

    async def ws_listener(self):
        """
        Asynchronously listens for messages from the WebSocket server and updates the measures.
        This method connects to the WebSocket server and processes incoming messages,
        updating the measures accordingly.
        """

        url = f'ws://{IP}:{PORT}'
        print(f"Connecting to WebSocket server at {url}...")
        async with connect(url) as ws:
            while True:
                msg = await ws.recv()
                parts = msg.split(RealtimeTrackerServer.TAG_SEPARATOR)
                if parts[0] == RealtimeTrackerServer.TAG_RPLIDAR_MEASURES:
                    self.measures = Measure.from_string_to_measures(parts[1])

if __name__ == "__main__":
    app = App()
    ws_thread = Thread(target=asyncio.run, args=(app.ws_listener(),), daemon=True)
    ws_thread.start()
    app.run()