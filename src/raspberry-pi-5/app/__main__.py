import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import RealtimeTrackerApp

if __name__ == "__main__":
    # Initialize the RealtimeTrackerApp
    realtime_tracker_app = RealtimeTrackerApp()