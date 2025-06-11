from websockets import connect
import asyncio
import tkinter as tk
import math

from server import RealtimeTrackerServer
from rplidar import RPLIDAR
from rplidar.measure import Measure

# Canvas and center point
SIZE = RPLIDAR.MAX_DISTANCE_LIMIT
CENTER_X = SIZE // 2
CENTER_Y = SIZE // 2

# Static circle padding
STATIC_CIRCLE_PADDING = 1000

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

# Function to plot points based on angle and distance
def plot_points(canvas: tk.Canvas, points: list[Measure]):
    """
    Plot points on the canvas based on their angle and distance from the center.
    Args:
        canvas (tk.Canvas): The Tkinter canvas to draw on.
        points (list[Measure]): List of Measure objects containing angle and distance.
    """
    # Clear previous points
    canvas.delete("all")

    # Draw points
    for point in points:
        radian_angle = math.radians(point.angle)
        x = CENTER_X + point.distance * math.cos(radian_angle)
        y = CENTER_Y + point.distance * math.sin(radian_angle)
        canvas.create_oval(x - POINT_RADIUS, y - POINT_RADIUS, x + POINT_RADIUS, y + POINT_RADIUS, fill=POINT_COLOR)  # Small circle for each point


async def app():
    """
    A simple Tkinter application to visualize RPLIDAR measures.
    """
    # Tkinter setup
    root = tk.Tk()
    root.title("Klevor RPLIDAR GUI")

    canvas = tk.Canvas(root, width=SIZE, height=SIZE, bg="white")
    canvas.pack()

    # Draw central point
    canvas.create_oval(CENTER_X - CENTRAL_POINT_RADIUS, CENTER_Y - CENTRAL_POINT_RADIUS, CENTER_X + CENTRAL_POINT_RADIUS, CENTER_Y + CENTRAL_POINT_RADIUS, fill=CENTRAL_POINT_COLOR)

    # Draw static circles
    n = SIZE / STATIC_CIRCLE_PADDING
    for i in range(1, n):
        radius = i * STATIC_CIRCLE_PADDING
        color = INTERNAL_STATIC_CIRCLE_COLOR if i < n else EXTERNAL_STATIC_CIRCLE_COLOR
        width = INTERNAL_STATIC_CIRCLE_WIDTH if i < n else EXTERNAL_STATIC_CIRCLE_WIDTH
        canvas.create_oval(
            CENTER_X - radius, CENTER_Y - radius,
            CENTER_X + radius, CENTER_Y + radius,
            outline=color, width=width
        )

    root.mainloop()

    # Connect to the server
    url = f'ws://{RealtimeTrackerServer.HOST}:{RealtimeTrackerServer.PORT}'
    print(f"Connecting to WebSocket server at {url}...")
    async with connect(url) as ws:
        # Stay alive forever, listen to incoming msgs
        while True:
            msg = await ws.recv()

            # Check if it's a message containing RPLIDAR measures
            parts = msg.split(RealtimeTrackerServer.TAG_SEPARATOR)

            if parts[0] == RealtimeTrackerServer.TAG_RPLIDAR_MEASURES:
                measures = Measure.from_string_to_measures(parts[1])
                print(f"Received RPLIDAR measures: {measures}")
                plot_points(canvas, measures)

if __name__ == "__main__":
    asyncio.run(app())
