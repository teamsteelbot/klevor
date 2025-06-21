from asyncio import create_task, gather

from .bno08x import BNO08XHandler
from .servo import ServoHandler
from .message import IncomingMessage, IncomingCategory, RPLIDAR
from .esc_motor import ESCMotorHandler
from .serial_communication import SerialCommunication

class Challenge:
    """
    Class to represent the enum challenge messages sent and received from the Raspberry Pi Pico.
    """

    WITH_OBSTACLES = "with_obstacles"
    WITHOUT_OBSTACLES = "without_obstacles"

    @classmethod
    def from_string(cls, challenge_str: str) -> str:
        """
        Convert a string to a Challenge enum value.

        Args:
            challenge_str (str): The string representation of the challenge.

        Returns:
            str: The corresponding Challenge enum value.
        """
        challenge_name = challenge_str.upper()
        for challenge in [cls.WITH_OBSTACLES, cls.WITHOUT_OBSTACLES]:
            if challenge_name == challenge:
                return challenge

        raise ValueError(f"Invalid challenge: {challenge_str}")


class WithoutObstacles:
    """
    Class for the WRO 2025 Challenge without Obstacles in the Future Engineers Car category.
    This class contains constants and methods related to the challenge.
    """

    # Distance constants
    FRONT_DISTANCE_THRESHOLD = 500
    SIDE_DISTANCE_DIFFERENCE_PERCENTAGE = 0.2
    SIDE_DISTANCE_THRESHOLD = 1500
    STOP_DISTANCE_THRESHOLD = 1500
    TARGET_DISTANCE_STOP_START = 200

    def __init__(self, bno08x: BNO08XHandler, servo: ServoHandler, motor: ESCMotorHandler,
                 serial_communication: SerialCommunication):
        """
        Initialize the WithoutObstacles class with the necessary handlers.

        Args:
            bno08x (BNO08XHandler): Handler for the BNO08X sensor.
            servo (ServoHandler): Handler for the servo motor.
            motor (ESCMotorHandler): Handler for the ESC motor.
            serial_communication (SerialCommunication): Handler for serial communication.
        """
        self.__bno08x = bno08x
        self.__servo = servo
        self.__motor = motor
        self.__serial_communication = serial_communication

        # Initialize the average distances
        self.__avg_front_dist, self.__avg_left_dist, self.__avg_right_dist = 0.0, 0.0, 0.0

    async def _calculate_distances(self, msgs: list[IncomingMessage]) -> None:
        """
        Calculate the average distances from the received RPLIDAR messages.

        Args:
            msgs (list[IncomingMessage]): List of incoming messages from the serial communication.
        """
        # Process the received messages (must be only RPLIDAR messages) on reverse order
        for msg in msgs[::-1]:
            if msg.category == IncomingCategory.RPLIDAR:
                # Split the message content to extract distance
                parts = msg.content.split(IncomingMessage.CONTENT_HEADER_SEPARATOR)

                # Check the type of distance
                if parts[0] == RPLIDAR.FRONT:
                    self.__avg_front_dist = float(parts[1])

                elif parts[0] == RPLIDAR.LEFT:
                    self.__avg_left_dist = float(parts[1])

                elif parts[0] == RPLIDAR.RIGHT:
                    self.__avg_right_dist = float(parts[1])

    async def loop(self):
        """
        Main loop for the challenge without obstacles.
        This function will continuously check the distances and control the robot's movements accordingly.
        """
        # Set the last known turns to zero
        last_known_turns = 0

        while True:
            # Create the update quaternion and receive serial messages tasks
            update_quaternion_task = create_task(self.__bno08x.update_quaternion())
            receive_serial_task = create_task(self.__serial_communication.receive_messages())

            # Wait for the tasks to complete
            results = await gather(update_quaternion_task, receive_serial_task)
            msgs = results[1]

            # Process the received messages (must be only RPLIDAR messages) on reverse order
            await self._calculate_distances(msgs)

            # Algorithm tasks
            tasks = []

            # Check for the current turn and center the servo if necessary
            if self.__servo.is_turning() and self.__bno08x.turns != last_known_turns:
                tasks.append(create_task(self.__servo.center()))

                # Update for the next check
                last_known_turns = self.__bno08x.turns

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
                        await self.__motor.stop()
                        await self.__serial_communication.stop()
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

            # Gather the tasks and wait for them to complete
            if tasks:
                await gather(*tasks)

class WithObstacles:
    """
    Class for the WRO 2025 Challenge with Obstacles in the Future Engineers Car category.
    This class contains constants and methods related to the challenge.
    """

    def __init__(self, bno08x: BNO08XHandler, servo: ServoHandler, motor: ESCMotorHandler,
                 serial_communication: SerialCommunication):
        """
        Initialize the WithObstacles class with the necessary handlers.

        Args:
            bno08x (BNO08XHandler): Handler for the BNO08X sensor.
            servo (ServoHandler): Handler for the servo motor.
            motor (ESCMotorHandler): Handler for the ESC motor.
            serial_communication (SerialCommunication): Handler for serial communication.
        """
        self.__bno08x = bno08x
        self.__servo = servo
        self.__motor = motor
        self.__serial_communication = serial_communication

    async def loop(self):
        """
        Main loop for the challenge with obstacles.
        This function will continuously check the distances and control the robot's movements accordingly.
        """
        pass