import argparse

from .args import Args
from .spawner import Spawner

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Klevor - WRO 2025 - Future Engineers Car"
    )
    args = Args(parser)
    args.add_yolo_version_argument()
    args.add_debug_argument()
    args.add_movement_argument()

    # Get the YOLO version
    arg_yolo_version = args.get_yolo_version()

    # Get the debug mode
    arg_debug = args.get_debug()

    # Get the movement flag
    arg_movement = args.get_movement()

    # Create the spawner instance
    spawner = Spawner(movement=arg_movement,
                        yolo_version=arg_yolo_version,
                        debug=arg_debug)

    # Spawn the processes
    spawner.run()