from multiprocessing import Event, Queue, RLock
from multiprocessing.sharedctypes import Value as ValueCls
from multiprocessing.synchronize import Event as EventCls
from queue import Empty
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
    SAFETY_FRONT_DISTANCE_THRESHOLD,
)
from ..common.measure import Measure
from ..enums import Challenge
from ..log import Logger
from ..log.decorators import log_on_error
from ..log.protocols import LoggerConsumerProtocol
from .enums import Direction
from ..serial_communication.dispatcher import Dispatcher as SerialDispatcher
from ..utils.decorators import ignore_sigint


class Pilot(PilotABC, LoggerConsumerProtocol):
    """
    Class for the Pilot handler.

    This class defines the interface for a Pilot handler, which is responsible for
    controlling the robot's movements.
    """

    # Logger configuration
    LOGGER_TAG = "Pilot"

    # Start delay
    START_DELAY = 5

    # RPLidar wait delay
    RPLIDAR_WAIT_DELAY = 0.1

    # Update delay
    MOTOR_DELAY = 0.2
    SERVO_DELAY = 0.05
    GYROSCOPE_DELAY = 0.05

    # Wait timeout for the start event
    START_WAIT_TIMEOUT = 0.1

    def __init__(
        self,
        debug: bool,
        challenge: ValueCls,
        start_event: EventCls,
        parking_event: EventCls,
        stop_event: EventCls,
        completed_event: EventCls,
        rplidar_update_measures_event: EventCls,
        rplidar_measures_queue: Queue,
        serial_sender_messages_queue: Queue,
        writer_messages_queue: Queue,
        bno08x_yaw_deg: ValueCls,
        bno08x_turns: ValueCls,
        movement: bool = True,
        photographer_capture_image_event: Optional[EventCls] = None,
        detector_model_g_inferences_queue: Optional[Queue] = None,
        detector_model_m_inferences_queue: Optional[Queue] = None,
        detector_model_r_inferences_queue: Optional[Queue] = None,
    ):
        """
        Initialize the Pilot class.

        Args:
            debug (bool): Flag to indicate if the pilot is in debug mode.
            challenge (ValueCls): Shared value to hold the current challenge.
            start_event (EventCls): Event to signal when the pilot should start.
            parking_event (EventCls): Event to signal the parking state of the robot.
            stop_event (EventCls): Event to signal when the pilot should stop.
            completed_event (EventCls): Event to signal when the challenge has been completed successfully.
            rplidar_update_measures_event (EventCls): Event to signal when the RPLidar should update measures.
            rplidar_measures_queue (Queue): Queue to hold RPLidar measures.
            serial_sender_messages_queue (Queue): Queue to hold outgoing messages to the serial port.
            writer_messages_queue (Queue): Queue to hold log messages.
            bno08x_yaw_deg (ValueCls): Shared value for the BNO08X yaw angle in degrees.
            bno08x_turns (ValueCls): Shared value for the BNO08X turns.
            movement (bool): Flag to indicate if the pilot should handle movement.
            photographer_capture_image_event (Optional[EventCls]): Event to signal when the photographer should capture an image.
            detector_model_g_inferences_queue (Optional[Queue]): Queue for model G inferences.
            detector_model_m_inferences_queue (Optional[Queue]): Queue for model M inferences.
            detector_model_r_inferences_queue (Optional[Queue]): Queue for model R inferences.
        """
        # Initialize the debug flag
        self.__debug = debug

        # Initialize the values, queues and events
        self.__challenge = challenge
        self.__started_event = Event()
        self.__start_event = start_event
        self.__parking_event = parking_event
        self.__deleted_event = Event()
        self.__stop_event = stop_event
        self.__completed_event = completed_event
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
            serial_sender_messages_queue
            )

        # Initialize the logger
        self.__logger = Logger(
            writer_messages_queue,
            tag=self.LOGGER_TAG,
            debug=self.__debug
            )

        # Initialize the reentrant lock
        self.__rlock = RLock()

        # Initialize the motor speed, servo angle and movement state
        self.__motor_speed = 0.0
        self.__servo_angle = SERVO_CENTER_ANGLE
        self.__movement = movement

        # Initialize the updated flags
        self.__motor_speed_updated = False
        self.__servo_angle_updated = False

        # Initialize the average distances dictionary
        self.__average_distances = {direction: 0.0 for direction in Direction}

    @final
    @property
    def logger(self) -> Logger:
        return self.__logger

    @final
    def _set_motor_speed(self, speed: float):
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
            self.__motor_speed_updated = True

        # Log
        self.__logger.info(f"Set motor speed to: {speed}")

    @final
    def _set_motor_stop(self):
        """
        Sets the speed of the ESC motor to 0.
        """
        self._set_motor_speed(0.0)

    @final
    def _set_motor_forward(self, speed: float):
        self._check_motor_speed_half_range(speed)
        self._set_motor_speed(speed)

    @final
    def _set_motor_backward(self, speed: float):
        self._check_motor_speed_half_range(speed)
        self._set_motor_speed(-speed)

    @final
    def _set_servo_angle(self, angle: int):
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
            self.__servo_angle_updated = True

        # Log
        self.__logger.info(f"Set servo angle to: {angle}deg")

    @final
    def _set_servo_angle_relative_to_center(self, relative_angle: int):
        if not (SERVO_LEFT_LIMIT <= relative_angle <= SERVO_RIGHT_LIMIT):
            raise ValueError(
                f"Relative angle must be between {SERVO_LEFT_LIMIT} and"
                f" {SERVO_RIGHT_LIMIT} degrees"
            )

        self._set_servo_angle(SERVO_CENTER_ANGLE + relative_angle)

    @final
    def _set_servo_to_center(self):
        self._set_servo_angle(SERVO_CENTER_ANGLE)

    @final
    def _set_servo_to_right(self, angle):
        if not 0 < angle <= SERVO_RIGHT_LIMIT:
            raise ValueError(
                f"Angle must be between 0 and {SERVO_RIGHT_LIMIT} degrees for right movement"
            )

        self._set_servo_angle(SERVO_CENTER_ANGLE + angle)

    @final
    def _set_servo_to_left(self, angle):
        if not 0 < angle <= abs(SERVO_LEFT_LIMIT):
            raise ValueError(
                f"Angle must be between 0 and {abs(SERVO_LEFT_LIMIT)} degrees for left movement"
            )

        self._set_servo_angle(SERVO_CENTER_ANGLE - angle)

    @final
    def _is_servo_turning(self):
        return self.__servo_angle != SERVO_CENTER_ANGLE

    @final
    def _get_rplidar_measures(self) -> dict[int, Measure] | None:
        # Set the event to signal that the RPLidar should update measures
        self.__rplidar_update_measures_event.set()

        # Get the measures from the queue
        while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
            try:
                return self.__rplidar_measures_queue.get(
                    timeout=self.RPLIDAR_WAIT_DELAY
                    )

            except Empty:
                continue

    @final
    def _update_rplidar_average_distances(self) -> None:
        # Get the RPLidar measures
        measures = self._get_rplidar_measures()
        if measures is None:
            raise TimeoutError(
                "RPLidar measures could not be retrieved within the timeout."
            )

        # Calculate the average distances according to the challenge
        if self.__challenge.value == Challenge.WITHOUT_OBSTACLES.as_char:
            # Calculate the average north, west and east distances
            self.__average_distances = self._calculate_average_distance(
                measures,
                Direction.NORTH,
                Direction.WEST,
                Direction.EAST
            )

        elif self.__challenge.value == Challenge.WITH_OBSTACLES.as_char:
            raise NotImplementedError(
                "Challenge with obstacles is not implemented yet."
            )

        else:
            raise ValueError(f"Unknown challenge: {self.__challenge.value}")

    def _calculate_sleep_delay(
            self,
            start_time: float
        ) -> float:
        """
        Calculate the sleep delay based on the start time and the update delay.

        Args:
            start_time (float): The start time in seconds.
        Returns:
            float: The calculated sleep delay.
        """
        # Determine the update delay based on the commands sent
        if self.__motor_speed_updated:
            update_delay = self.MOTOR_DELAY
        elif self.__servo_angle_updated:
            update_delay = self.SERVO_DELAY
        else:
            update_delay = self.GYROSCOPE_DELAY

        # Reset the updated flags
        self.__motor_speed_updated = False
        self.__servo_angle_updated = False

        # Calculate the elapsed time since the start time
        elapsed_time = monotonic() - start_time
        delay = update_delay - elapsed_time
        return 0.0 if delay < 0 else delay

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

        while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
            # Get the start time
            start_time = monotonic()

            # Get the average distances from the RPLidar
            self._update_rplidar_average_distances()
            west_avg_dist = self.__average_distances[Direction.WEST]
            east_avg_dist = self.__average_distances[Direction.EAST]
            north_avg_dist = self.__average_distances[Direction.NORTH]
            self.__logger.debug(
                f"North: {north_avg_dist}, West: {west_avg_dist}, East: {east_avg_dist}"
            )

            # Check if the front distance is below the safety threshold
            if north_avg_dist < SAFETY_FRONT_DISTANCE_THRESHOLD:
                self.__logger.warning(
                    f"Front distance {north_avg_dist} is below the safety threshold."
                )
                self._set_motor_backward(MOTOR_SPEED_NORMAL)
                self._set_servo_to_center()

                # Sleep for a short time before checking again
                self._sleep(start_time)
                continue

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
                    self._update_rplidar_average_distances()
                    north_avg_dist = self.__average_distances[Direction.NORTH]

                    if north_avg_dist <= STOP_DISTANCE_THRESHOLD:
                        # Set the completed event
                        self.__completed_event.set()

                        # Stop the motor
                        self._set_motor_stop()

                        self.__logger.info(
                            "Challenge completed successfully. Stopping the robot."
                        )

                        # Sleep for a short time before exiting
                        self._sleep(start_time)
                        return

                    # Sleep for a short time before checking again
                    self._sleep(start_time)

            # Check if one of them is 0
            if (north_avg_dist == 0 or
                    west_avg_dist == 0 or east_avg_dist == 0):
                self.__logger.warning(
                    "One of the average distances is 0. This may cause unexpected behavior. Waiting for new measures..."
                )

                # Sleep
                self._sleep(start_time)
                continue

            # Check if the robot should move forward or turn
            if north_avg_dist >= FRONT_DISTANCE_THRESHOLD:
                self._set_motor_speed(MOTOR_SPEED_NORMAL)

                # Check if the servo should make a little turn to the left or right in order to center the robot
                if east_avg_dist >= west_avg_dist * (
                        1 + SIDE_DISTANCE_DIFFERENCE_PERCENTAGE):
                    self._set_servo_to_right(SERVO_SMALL_TURN_ANGLE)

                elif west_avg_dist >= east_avg_dist * (
                        1 + SIDE_DISTANCE_DIFFERENCE_PERCENTAGE):
                    self._set_servo_to_left(SERVO_SMALL_TURN_ANGLE)

                else:
                    self._set_servo_to_center()

            else:
                self._set_motor_speed(MOTOR_SPEED_SLOW)

                # Check if the robot should turn left or right based on the side distances
                if east_avg_dist >= SIDE_DISTANCE_THRESHOLD:
                    self._set_servo_to_right(SERVO_BIG_TURN_ANGLE)

                elif west_avg_dist >= SIDE_DISTANCE_THRESHOLD:
                    self._set_servo_to_left(SERVO_BIG_TURN_ANGLE)

            # Sleep for the calculated delay
            self._sleep(start_time)

    @final
    def _start(self):
        with self.__rlock:
            # Check if the stop event is set
            if self.__stop_event.is_set():
                raise RuntimeError(
                    "Stop event is set. Pilot will not run."
                )

            # Check if the Pilot is already running
            if self.__started_event.is_set():
                raise RuntimeError(
                    "Pilot is already running. Cannot start again."
                )

            # Set the started event to signal that the Pilot has started
            self.__started_event.set()

        # Log
        self.__logger.info("Initialized.")

    @final
    def _stop(self):
        with self.__rlock:
            # Clear the started event
            self.__started_event.clear()

            # Clear the deleted event
            self.__deleted_event.clear()

            # Set the stop event
            self.__stop_event.set()

        # Log
        self.__logger.info("Stopped.")

    @final
    @ignore_sigint
    @log_on_error()
    def run(self):
        # Start the pilot
        self._start()

        # Wait for the start event to be set
        self.__logger.info("Waiting for the start event...")
        while not self.__stop_event.is_set() and not self.__deleted_event.is_set():
            if self.__start_event.wait(timeout=self.START_WAIT_TIMEOUT):
                break
        if self.__stop_event.is_set() or self.__deleted_event.is_set():
            # Stop the Pilot if the stop or deleted event is set
            self._stop()
            return
        self.__logger.info("Started.")

        try:
            # Start the corresponding challenge handler
            if self.__challenge.value == Challenge.WITHOUT_OBSTACLES.as_char:
                self._challenge_without_obstacles()
            elif self.__challenge.value == Challenge.WITH_OBSTACLES.as_char:
                self._challenge_with_obstacles()
            else:
                raise ValueError(
                    f"Unknown challenge: {self.__challenge.value}"
                )

            # Stop the Pilot
            self._stop()

        except Exception as e:
            # Stop the Pilot in case of an exception
            self._stop()
            raise e

    def __del__(self):
        """
        Destructor to clean up resources when the Pilot is no longer needed.
        """
        self.__deleted_event.set()

        # Log
        self.__logger.info(
            "Instance is being deleted. Resources will be cleaned up."
        )
