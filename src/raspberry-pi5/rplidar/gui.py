from websockets import connect
import asyncio
import tkinter as tk
import math
from threading import Thread
from time import sleep

from server import RealtimeTrackerServer
from rplidar import RPLIDAR
from rplidar.measure import Measure

# IP and port for the WebSocket server
IP = "0.0.0.0"
PORT = 8765

# Constants for the RPLIDAR GUI
APP_SIZE = 800

# Canvas and center point
SIZE_FACTOR = APP_SIZE / RPLIDAR.MAX_DISTANCE_LIMIT
RADIUS = APP_SIZE // 2
CENTER_X = APP_SIZE // 2
CENTER_Y = APP_SIZE // 2

# Static circle padding
STATIC_CIRCLE_PADDING = 1000 * SIZE_FACTOR

# Internal static circle color
INTERNAL_STATIC_CIRCLE_COLOR = "lightgray"

# Internal static circle width
INTERNAL_STATIC_CIRCLE_WIDTH = 1

# External static circle color
EXTERNAL_STATIC_CIRCLE_COLOR = "black"

# External static circle width
EXTERNAL_STATIC_CIRCLE_WIDTH = 3

# Central point radius
CENTRAL_POINT_RADIUS = 5

# Point radius
POINT_RADIUS = 2

# Central point color
CENTRAL_POINT_COLOR = "blue"

# Point color
POINT_COLOR = "red"

# Canvas update delay
UPDATE_DELAY = 1000

# Distance minimum difference to consider a point as new
DISTANCE_MINIMUM_DIFFERENCE = 10

class App():
    """
    A simple Tkinter application to visualize RPLIDAR measures.
    """
    def __init__(self):
        # Tkinter setup
        self.root = tk.Tk()
        self.root.title("Klevor RPLIDAR GUI")

        self.canvas = tk.Canvas(self.root, width=APP_SIZE, height=APP_SIZE, bg="white")
        self.canvas.pack()

        # Initialize measures list
        self.measures = []

        # Initialize previous measures map to track changes
        self.previous_measures = {}

        # Create points IDs map
        self.point_ids = {}

        # Draw central point
        self.canvas.create_oval(CENTER_X - CENTRAL_POINT_RADIUS, CENTER_Y - CENTRAL_POINT_RADIUS, CENTER_X + CENTRAL_POINT_RADIUS, CENTER_Y + CENTRAL_POINT_RADIUS, fill=CENTRAL_POINT_COLOR)

        # Draw static circles
        n = int(APP_SIZE / STATIC_CIRCLE_PADDING)
        is_exact = APP_SIZE % STATIC_CIRCLE_PADDING == 0
        for i in range(1, n):
            radius = i * STATIC_CIRCLE_PADDING
            color = INTERNAL_STATIC_CIRCLE_COLOR if i == n and is_exact else EXTERNAL_STATIC_CIRCLE_COLOR
            width = INTERNAL_STATIC_CIRCLE_WIDTH if i == n and is_exact else EXTERNAL_STATIC_CIRCLE_WIDTH
            self.canvas.create_oval(
                CENTER_X - radius, CENTER_Y - radius,
                CENTER_X + radius, CENTER_Y + radius,
                outline=color, width=width
            )
        
        self.canvas.create_oval(
            CENTER_X - RADIUS, CENTER_Y - RADIUS,
            CENTER_X + RADIUS, CENTER_Y + RADIUS,
            outline=EXTERNAL_STATIC_CIRCLE_COLOR, width=EXTERNAL_STATIC_CIRCLE_WIDTH
        )

        self.root.after(UPDATE_DELAY, self.update_canvas)

    def update_points(self):
        # Update or create points based on angle
        for measure in self.measures:
            # Check if the measure is new or has changed significantly
            if measure in self.previous_measures:
                previous_measure = self.previous_measures.get(measure.angle)
                if previous_measure and abs(previous_measure.distance - measure.distance) < DISTANCE_MINIMUM_DIFFERENCE:
                    # Skip if the distance hasn't changed significantly
                    continue

            # Update the previous measure
            self.previous_measures[measure.angle] = measure

            # Calculate the position of the point based on the angle and distance
            radian_angle = math.radians(measure.angle)
            x = CENTER_X + measure.distance * math.cos(radian_angle) * SIZE_FACTOR
            y = CENTER_Y + measure.distance * math.sin(radian_angle) * SIZE_FACTOR

            if measure.angle in self.point_ids:
                # Move existing point
                point_id = self.point_ids.get(measure.angle)
                self.canvas.coords(point_id, x - POINT_RADIUS, y - POINT_RADIUS, x + POINT_RADIUS, y + POINT_RADIUS)
            else:
                # Create new point
                point_id = self.canvas.create_oval(
                    x - POINT_RADIUS, y - POINT_RADIUS, x + POINT_RADIUS, y + POINT_RADIUS,
                    fill=POINT_COLOR
                )
                self.point_ids[measure.angle] = point_id

        """
        # Remove points for angles not in the new measures
        current_angles = set(m.angle for m in measures)
        for angle in list(self.point_ids):
            if angle not in current_angles:
                self.canvas.delete(self.point_ids[angle])
                del self.point_ids[angle]
        """

    def update_canvas(self):
        if self.measures:
            self.update_points()
        self.root.after(UPDATE_DELAY, self.update_canvas)

    async def ws_listener(self):
        url = f'ws://{IP}:{PORT}'
        print(f"Connecting to WebSocket server at {url}...")
        async with connect(url) as ws:
            # Stay alive forever, listen to incoming msgs
            while True:
                msg = await ws.recv()

                # Check if it's a message containing RPLIDAR measures
                parts = msg.split(RealtimeTrackerServer.TAG_SEPARATOR)

                if parts[0] == RealtimeTrackerServer.TAG_RPLIDAR_MEASURES:
                    self.measures = Measure.from_string_to_measures(parts[1])

if __name__ == "__main__":
    app = App()

    # Create a thread for the WebSocket listener
    ws_thread = Thread(target=asyncio.run, args=(app.ws_listener(),))
    ws_thread.start()

    # Start the Tkinter main loop
    app.root.mainloop()