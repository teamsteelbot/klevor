import argparse

from .args import Args
from .args.enums import Flag
from .challenge import ChallengeHandler
from .env import Env

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Klevor - WRO 2025 - Future Engineers Car"
    )
    Args.add_yolo_version_argument(parser)
    Args.add_debug_argument(parser)
    args = Args.parse_args_as_dict(parser)

    # Get the YOLO version
    arg_yolo_version = Args.get_attribute_from_args_dict(args, Flag.VERSION)

    # Get the debug mode
    arg_debug = Args.get_attribute_from_args_dict(args, Flag.DEBUG)

    # Set the debug mode and YOLO version as environment variables
    Env.set_yolo_version(arg_yolo_version)
    Env.set_debug_mode(arg_debug)

    # Create the challenge instance
    challenge_handler = ChallengeHandler()

    # Spawn the processes
    challenge_handler.spawn_processes()

    # Wait for the start event to be set
    challenge_handler.wait_start_event()

    # Wait for the stop event to be set
    challenge_handler.wait_stop_event()
