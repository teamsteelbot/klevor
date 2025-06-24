from multiprocessing import Queue, Event, Value
from typing import final, Optional

from ..log import Logger
from .constants import SERVO_CENTER_ANGLE, SERVO_RIGHT_LIMIT, SERVO_LEFT_LIMIT
from ..serial_communication.dispatcher import Dispatcher as SerialDispatcher
from .abstracts import PilotABC

class Pilot(PilotABC):
    """
    Class for the Pilot handler.

    This class defines the interface for a Pilot handler, which is responsible for
    controlling the robot's movements.
    """

    # Logger configuration
    LOGGER_TAG = "Pilot"

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
            RPLIDAR should update measures.
            rplidar_measures_queue (Queue): Queue to hold RPLIDAR measures.
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
        self.__opened_event = Event()

        # Initialize the serial communication dispatcher
        self.__serial_dispatcher = SerialDispatcher(
            serial_incoming_messages_queue,
            serial_outgoing_messages_queue,
            writer_messages_queue
        )

        # Initialize the logger
        self.__logger = Logger(writer_messages_queue, self.LOGGER_TAG)

        # Initialize the motor speed, servo angle and movement state
        self.__motor_speed = 0.0
        self.__servo_angle = SERVO_CENTER_ANGLE
        self.__movement = movement


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
            self.__serial_dispatcher.send_motor_speed_message(self.__motor_speed)

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
            self.__serial_dispatcher.send_servo_angle_message(self.__servo_angle)

        # Log
        self.__logger.info(f"Set servo angle to: {angle}deg")

    @final
    async def _set_servo_angle_relative_to_center(self, relative_angle: int):
        if not (SERVO_LEFT_LIMIT <= relative_angle <= SERVO_RIGHT_LIMIT):
            raise ValueError(
                f"Relative angle must be between {SERVO_LEFT_LIMIT} and"
                f" {SERVO_RIGHT_LIMIT} degrees")

        await self._set_servo_angle(SERVO_CENTER_ANGLE + relative_angle)

    @final
    async def _set_servo_to_center(self):
        await self._set_servo_angle(SERVO_CENTER_ANGLE)

    @final
    async def _set_servo_to_right(self, angle):
        if not 0 < angle <= SERVO_RIGHT_LIMIT:
            raise ValueError(
                f"Angle must be between 0 and {SERVO_RIGHT_LIMIT} degrees for right movement")

        await self._set_servo_angle(SERVO_CENTER_ANGLE + angle)

    @final
    async def _set_servo_to_left(self, angle):
        if not 0 < angle <= abs(SERVO_LEFT_LIMIT):
            raise ValueError(
                f"Angle must be between 0 and {abs(SERVO_LEFT_LIMIT)} degrees for left "
                f"movement")

        await self._set_servo_angle(SERVO_CENTER_ANGLE - angle)

    @final
    def _is_servo_turning(self):
        return self.__servo_angle != SERVO_CENTER_ANGLE

"""
after rotation


# Put the parsed line in the server
        if self.__server:
            for angle, measure in self.__distances_dict.items():
                measure_str = str(measure)
                self.__server.broadcast_rplidar_measures(str(measure))

        # Send the measure string to the serial communication
        if self.__serial_communication:
            if self.__challenge == Challenge.WITHOUT_OBSTACLES:
                # Calculate the average front, left and right distances by 5 degrees to each side
                avg_front_dist = self._calculate_average_distance(
                    [*range(355, 360), *range(0, 6)])
                avg_left_dist = self._calculate_average_distance(
                    [*range(265, 276)])
                avg_right_dist = self._calculate_average_distance(
                    [*range(85, 96)])

                # Create a dictionary with the average distances
                avg_distances = {
                    RPLIDARKey.FRONT: avg_front_dist,
                    RPLIDARKey.LEFT: avg_left_dist,
                    RPLIDARKey.RIGHT: avg_right_dist
                }

                # Send the average distances to the serial communication
                self.__serial_communication.send_rplidar_measures(avg_distances)
                
                
                
                
                 # Check for the current turn and center the servo if necessary
            if self.__servo.is_turning():
                if self.__bno08x.turns != last_known_turns:
                    tasks.append(create_task(self.__servo.center()))

                    # Update for the next check
                    last_known_turns = self.__bno08x.turns
                continue

            # Overall Mission Completion Check
            if last_known_turns == 12:
                tasks.append(create_task(self.__motor.set_speed(self.__motor.SPEED_NORMAL)))

                # Gather the tasks and wait for them to complete
                await gather(*tasks)

                while True:
                    # Receive messages from the serial communication
                    msgs = await self.__serial_communication.receive_messages()

                    # Process the received messages (must be only RPLIDAR messages) on reverse order
                    await self._calculate_distances(msgs)

                    if self.__avg_front_dist <= self.STOP_DISTANCE_THRESHOLD:
                        
                        return

            # Check if the robot should move forward or turn
            if self.__avg_front_dist >= self.FRONT_DISTANCE_THRESHOLD:
                tasks.append(create_task(self.__motor.set_speed(self.__motor.SPEED_NORMAL)))

                # Check if the servo should make a little turn to the left or right in order to center the robot
                if self.__avg_right_dist >= self.__avg_left_dist * (1 + self.SIDE_DISTANCE_DIFFERENCE_PERCENTAGE):
                    tasks.append(create_task(self.__servo.right(self.__servo.SMALL_TURN_ANGLE)))

                elif self.__avg_left_dist >= self.__avg_right_dist * (1 + self.SIDE_DISTANCE_DIFFERENCE_PERCENTAGE):
                    tasks.append(create_task(self.__servo.left(self.__servo.SMALL_TURN_ANGLE)))

                else:
                    tasks.append(create_task(self.__servo.center()))

            else:
                tasks.append(create_task(self.__motor.set_speed(self.__motor.SPEED_SLOW)))

                # Check if the robot should turn left or right based on the side distances
                if self.__avg_right_dist >= self.SIDE_DISTANCE_THRESHOLD:
                    tasks.append(create_task(self.__servo.right(self.__servo.BIG_TURN_ANGLE)))

                elif self.__avg_left_dist >= self.SIDE_DISTANCE_THRESHOLD:
                    tasks.append(create_task(self.__servo.left(self.__servo.BIG_TURN_ANGLE)))

"""