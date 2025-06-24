import argparse

from .args import Args
from .args.enums import Flag
from .spawner import Spawner
from .env import Env

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Klevor - WRO 2025 - Future Engineers Car"
    )
    Args.add_yolo_version_argument(parser)
    Args.add_debug_argument(parser)
    Args.add_movement_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args_dict(args, Flag.VERSION)

    # Get the debug mode
    arg_debug = Args.get_attribute_from_args_dict(args, Flag.DEBUG)

    # Get the movement flag
    arg_movement = Args.get_attribute_from_args_dict(args, Flag.MOVEMENT)

    # Set the debug mode and YOLO version as environment variables
    Env.set_yolo_version(arg_yolo_version)
    Env.set_debug_mode(arg_debug)

    # Create the spawner instance
    spawner = Spawner(movement=arg_movement)

    # Spawn the processes
    spawner.run()
