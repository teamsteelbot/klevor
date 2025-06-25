from queue import Empty
from multiprocessing import Event, Queue, RLock, Value
from time import monotonic, sleep
from typing import Optional, final

from .abstracts import PilotABC
from .constants import (
    FRONT_DISTANCE_THRESHOLD,
    MOTOR_SPEED_NORMAL,
    MOTOR_SPEED_SLOW,
    SERVO_BIG_TURN_ANGLE,
    SERVO_CENTER_ANGLE,
    SERVO_LEFT_LIMIT,
    SERVO_RIGHT_LIMIT,
    SERVO_SMALL_TURN_ANGLE,
    SIDE_DISTANCE_DIFFERENCE_PERCENTAGE,
    SIDE_DISTANCE_THRESHOLD,
    STOP_DISTANCE_THRESHOLD,
    TURNS,
)
from ..env import Env
from ..env.enums import Challenge
from ..log import Logger
from ..rplidar import RPLidar
from ..rplidar.enums import Direction
from ..rplidar.measure import Measure
from ..serial_communication.dispatcher import Dispatcher as SerialDispatcher
from ..utils.decorators import ignore_sigint, log_method_error


class Pilot(PilotABC):
    """
    Class for the Pilot handler.

    This class defines the interface for a Pilot handler, which is responsible for
    controlling the robot's movements.
    """

    # Logger configuration
    LOGGER_TAG = "Pilot"

    # Wait delay
    WAIT_DELAY = 0.1

    # Update delay
    UPDATE_DELAY = 0.2

    def __init__(
        self,
        start_event: Event,
        parking_event: Event,
        stop_event: Event,
        rplidar_update_measures_event: Event,
        rplidar_measures_queue: Queue,
        serial_incoming_messages_queue: Queue,
        serial_outgoing_messages_queue: Queue,
        writer_messages_queue: Queue,
        bno08x_yaw_deg: Value,
        bno08x_turns: Value,
        movement: bool = True,
        photographer_capture_image_event: Optional[Event] = None,
        detector_model_g_inferences_queue: Optional[Queue] = None,
        detector_model_m_inferences_queue: Optional[Queue] = None,
        detector_model_r_inferences_queue: Optional[Queue] = None,
    ):
        """
        Initialize the Pilot class.

        Args:
            start_event (Event): Event to signal when the pilot should start.
            parking_event (Event): Event to signal the parking state of the robot.
            stop_event (Event): Event to signal when the pilot should stop.
            rplidar_update_measures_event (Event): Event to signal when the
            RPLidar should update measures.
            rplidar_measures_queue (Queue): Queue to hold RPLidar measures.
            serial_incoming_messages_queue (Queue): Queue to hold incoming messages from the serial port.
            serial_outgoing_messages_queue (Queue): Queue to hold outgoing messages to the serial port.
            writer_messages_queue (Queue): Queue to hold log messages.
            bno08x_yaw_deg (Value): Shared value for the BNO08X yaw angle in degrees.
            bno08x_turns (Value): Shared value for the BNO08X turns.
            movement (bool): Flag to indicate if the pilot should handle movement.
            photographer_capture_image_event (Optional[Event]): Event to signal when the photographer should capture an image.
            detector_model_g_inferences_queue (Optional[Queue]): Queue for model G inferences.
            detector_model_m_inferences_queue (Optional[Queue]): Queue for model M inferences.
            detector_model_r_inferences_queue (Optional[Queue]): Queue for model R inferences.
        """
        # Initialize the values, queues and events
        self.__started_event = Event()
        self.__start_event = start_event
        self.__parking_event = parking_event
        self.__stop_event = stop_event
        self.__rplidar_update_measures_event = rplidar_update_measures_event
        self.__rplidar_measures_queue = rplidar_measures_queue
        self.__photographer_capture_image_event = photographer_capture_image_event
        self.__detector_model_g_inferences_queue = detector_model_g_inferences_queue
        self.__detector_model_m_inferences_queue = detector_model_m_inferences_queue
        self.__detector_model_r_inferences_queue = detector_model_r_inferences_queue
        self.__bno08x_yaw_deg = bno08x_yaw_deg
        self.__bno08x_turns = bno08x_turns

        # Initialize the serial communication dispatcher
        self.__serial_dispatcher = SerialDispatcher(
            serial_incoming_messages_queue,
            serial_outgoing_messages_queue,
            writer_messages_queue
        )

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the motor speed, servo angle and movement state
        self.__motor_speed = 0.0
        self.__servo_angle = SERVO_CENTER_ANGLE
        self.__movement = movement

        # Initialize the challenge
        self.__challenge = None

    @final
    async def _set_motor_speed(self, speed: float):
        # Check if the speed is the same as the current speed
        if self.__motor_speed == speed:
            return

        # Check if the speed is within the full range
        self._check_motor_speed_full_range(speed)
        self.__motor_speed = speed

        # Send the speed message to the serial communication
        if self.__movement:
            self.__serial_dispatcher.send_motor_speed_message(
                self.__motor_speed
            )

        # Log
        self.__logger.info(f"Set motor speed to: {speed}")

    @final
    async def _set_motor_stop(self):
        """
        Sets the speed of the ESC motor to 0.
        """
        await self._set_motor_speed(0.0)

    @final
    async def _set_motor_forward(self, speed: float):
        self._check_motor_speed_half_range(speed)
        await self._set_motor_speed(speed)

    @final
    async def _set_motor_backward(self, speed: float):
        self._check_motor_speed_half_range(speed)
        await self._set_motor_speed(-speed)

    @final
    async def _set_servo_angle(self, angle: int):
        # Check if the angle is the same as the current angle
        if self.__servo_angle == angle:
            return

        # Check if the angle is within the valid range
        self._check_servo_angle(angle)
        self.__servo_angle = angle

        if self.__movement:
            self.__serial_dispatcher.send_servo_angle_message(
                self.__servo_angle
            )

        # Log
        self.__logger.info(f"Set servo angle to: {angle}deg")

    @final
    async def _set_servo_angle_relative_to_center(self, relative_angle: int):
        if not (SERVO_LEFT_LIMIT <= relative_angle <= SERVO_RIGHT_LIMIT):
            raise ValueError(
                f"Relative angle must be between {SERVO_LEFT_LIMIT} and"
                f" {SERVO_RIGHT_LIMIT} degrees"
            )

        await self._set_servo_angle(SERVO_CENTER_ANGLE + relative_angle)

    @final
    async def _set_servo_to_center(self):
        await self._set_servo_angle(SERVO_CENTER_ANGLE)

    @final
    async def _set_servo_to_right(self, angle):
        if not 0 < angle <= SERVO_RIGHT_LIMIT:
            raise ValueError(
                f"Angle must be between 0 and {SERVO_RIGHT_LIMIT} degrees for right movement"
            )

        await self._set_servo_angle(SERVO_CENTER_ANGLE + angle)

    @final
    async def _set_servo_to_left(self, angle):
        if not 0 < angle <= abs(SERVO_LEFT_LIMIT):
            raise ValueError(
                f"Angle must be between 0 and {abs(SERVO_LEFT_LIMIT)} degrees for left movement"
            )

        await self._set_servo_angle(SERVO_CENTER_ANGLE - angle)

    @final
    def _is_servo_turning(self):
        return self.__servo_angle != SERVO_CENTER_ANGLE

    @final
    def _get_rplidar_measures(self) -> dict[int, Measure]:
        # Set the event to signal that the RPLidar should update measures
        self.__rplidar_update_measures_event.set()

        # Get the measures from the queue
        try:
            return self.__rplidar_measures_queue.get(timeout=self.WAIT_DELAY)

        except Empty:
            raise TimeoutError(
                "No RPLidar measures received within the timeout period."
            )

    @final
    def _get_rplidar_average_distances(self) -> dict[Direction, float]:
        # Get the RPLidar measures
        measures = self._get_rplidar_measures()

        # Calculate the average distances according to the challenge
        if self.__challenge == Challenge.WITHOUT_OBSTACLES:
            # Calculate the average front, left and right distances by 5 degrees to each side
            avg_front_dist = RPLidar.calculate_average_distance(
                measures, [*range(355, 360), *range(0, 6)]
            )
            avg_left_dist = RPLidar.calculate_average_distance(
                measures, [*range(265, 276)]
            )
            avg_right_dist = RPLidar.calculate_average_distance(
                measures, [*range(85, 96)]
            )

            # Create a dictionary with the average distances
            return {
                Direction.FRONT: avg_front_dist,
                Direction.LEFT: avg_left_dist,
                Direction.RIGHT: avg_right_dist
            }
        elif self.__challenge == Challenge.WITH_OBSTACLES:
            raise NotImplementedError(
                "Challenge with obstacles is not implemented yet."
            )

        else:
            raise ValueError(f"Unknown challenge: {self.__challenge}")

    def _calculate_sleep_delay(self, start_time: float) -> float:
        """
        Calculate the sleep delay based on the start time and the update delay.

        Args:
            start_time (float): The start time in seconds.

        Returns:
            float: The calculated sleep delay.
        """
        elapsed_time = monotonic() - start_time
        delay = self.UPDATE_DELAY - elapsed_time
        if delay < 0:
            return 0.0
        return delay

    def _sleep(self, start_time: float):
        """
        Sleep for the calculated delay based on the start time.

        Args:
            start_time (float): The start time in seconds.
        """
        sleep(self._calculate_sleep_delay(start_time))

    @final
    def _challenge_with_obstacles(self):
        raise NotImplementedError(
            "Challenge with obstacles is not implemented yet."
        )

    @final
    def _challenge_without_obstacles(self):
        # Initialize the last turns
        last_turns = self.__bno08x_turns.value

        while True:
            # Get the start time
            start_time = monotonic()

            # Check for the current turn and center the servo if necessary
            if self._is_servo_turning():
                turns = self.__bno08x_turns.value
                if turns != last_turns:
                    self._set_servo_to_center()

                    # Update for the next check
                    last_turns = turns

                # Sleep
                self._sleep(start_time)
                continue

            # Check if it's almost time to stop
            if last_turns == TURNS:
                self._set_servo_to_center()
                self._set_motor_speed(MOTOR_SPEED_SLOW)

                while True:
                    # Update the start time
                    start_time = monotonic()

                    # Get the average distances
                    avg_distances = self._get_rplidar_average_distances()

                    if (avg_distances[Direction.FRONT] <=
                            STOP_DISTANCE_THRESHOLD):
                        return

                    # Sleep for a short time before checking again
                    self._sleep(start_time)

            # Get the average distances from the RPLidar
            avg_distances = self._get_rplidar_average_distances()
            left_avg_dist = avg_distances[Direction.LEFT]
            right_avg_dist = avg_distances[Direction.RIGHT]
            front_avg_dist = avg_distances[Direction.FRONT]

            # Check if the robot should move forward or turn
            if front_avg_dist >= FRONT_DISTANCE_THRESHOLD:
                self._set_motor_speed(MOTOR_SPEED_NORMAL)

                # Check if the servo should make a little turn to the left or right in order to center the robot
                if right_avg_dist >= left_avg_dist * (
                        1 + SIDE_DISTANCE_DIFFERENCE_PERCENTAGE):
                    self._set_servo_to_right(SERVO_SMALL_TURN_ANGLE)

                elif left_avg_dist >= right_avg_dist * (
                        1 + SIDE_DISTANCE_DIFFERENCE_PERCENTAGE):
                    self._set_servo_to_left(SERVO_SMALL_TURN_ANGLE)

                else:
                    self._set_servo_to_center()

            else:
                self._set_motor_speed(MOTOR_SPEED_SLOW)

                # Check if the robot should turn left or right based on the side distances
                if right_avg_dist >= SIDE_DISTANCE_THRESHOLD:
                    self._set_servo_to_right(SERVO_BIG_TURN_ANGLE)

                elif left_avg_dist >= SIDE_DISTANCE_THRESHOLD:
                    self._set_servo_to_left(SERVO_BIG_TURN_ANGLE)

    @final
    @ignore_sigint
    @log_method_error('__logger')
    def run(self):
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                self.__logger.warning(
                    "Stop event is set. Pilot will not run."
                )
                return

            # Check if the Pilot is already running
            if self.__started_event.is_set():
                self.__logger.warning(
                    "Pilot is already running. Cannot start again."
                )
                return

            # Set the started event to signal that the Pilot has started
            self.__started_event.set()

        # Wait for the start event to be set
        self.__start_event.wait()

        # Get the challenge from the environment variables
        self.__challenge = Env.get_challenge()

        # Start the corresponding challenge handler
        self.__logger.debug("Pilot is starting...")
        if self.__challenge == Challenge.WITHOUT_OBSTACLES:
            self._challenge_without_obstacles()
        elif self.__challenge == Challenge.WITH_OBSTACLES:
            self._challenge_with_obstacles()
        else:
            raise ValueError(f"Unknown challenge: {self.__challenge}")

        # Send the stop event to signal that the Pilot should stop
        self.__stop_event.set()

        # Clear the started event
        with self.__rlock:
            self.__started_event.clear()

        # Log
        self.__logger.info("Pilot stopped.")

    def __del__(self):
        """
        Destructor to clean up resources when the Pilot is no longer needed.
        """
        self.__stop_event.set()

        # Log
        self.__logger.debug(
            "Pilot instance is being deleted. Resources will be cleaned up."
        )
