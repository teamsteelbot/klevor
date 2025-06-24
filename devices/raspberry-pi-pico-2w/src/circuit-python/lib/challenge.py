from asyncio import create_task, gather
from time import monotonic

from .bno08x import BNO08XHandler
from .esc_motor import ESCMotorHandler
from .message import IncomingCategory, IncomingMessage
from .serial_communication import SerialCommunication
from .servo import ServoHandler


class WithoutObstacles:
    """
    Class for the WRO 2025 Challenge without Obstacles in the Future Engineers Car category.
    This class contains constants and methods related to the challenge.
    """
    # Receiving message timeout
    RECEIVING_MESSAGE_TIMEOUT = 10.0

    def __init__(
        self,
        bno08x: BNO08XHandler,
        servo: ServoHandler,
        motor: ESCMotorHandler,
        serial_communication: SerialCommunication
        ):
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

    async def loop(self):
        """
        Main loop for the challenge without obstacles.
        This function will continuously check the distances and control the robot's movements accordingly.
        """
        # Set the exit condition to False
        to_exit = False

        # Get start time to compare with the timeout
        start_time = monotonic()

        while not to_exit:
            # Create the update quaternion and receive serial messages tasks
            update_quaternion_task = create_task(
                self.__bno08x.update_quaternion()
                )
            receive_serial_task = create_task(
                self.__serial_communication.receive_messages()
                )

            # Wait for the tasks to complete
            results = await gather(update_quaternion_task, receive_serial_task)
            msgs: list[IncomingMessage] = results[1]
            if len(msgs) == 0:
                # If no messages were received, check if the timeout has been reached
                if monotonic() - start_time > self.RECEIVING_MESSAGE_TIMEOUT:
                    raise TimeoutError(
                        "No messages received within the timeout period."
                    )
            else:
                # Reset the start time if messages are received
                start_time = monotonic()

            # Algortihm tasks
            tasks = []

            # Process the received messages
            motor_speed = None
            servo_angle = None
            for msg in msgs:
                if msg == SerialCommunication.STOP_MESSAGE:
                    # Set the exit condition to True
                    to_exit = True

                    # Stop the motor and center the servo
                    tasks.append(create_task(self.__motor.stop()))
                    tasks.append(create_task(self.__servo.center()))

                    # Send a confirmation message to the serial communication
                    tasks.append(
                        create_task(
                            self.__serial_communication.send_confirmation_message()
                        )
                    )
                    break

                elif msg.category == IncomingCategory.MOTOR_SPEED:
                    # Set the motor speed
                    motor_speed = float(msg.content)

                elif msg.category == IncomingCategory.SERVO_ANGLE:
                    # Set the servo angle
                    servo_angle = int(msg.content)

            # Add the set motor speed task and set servo angle task if the exit flag is not set
            if not to_exit:
                if motor_speed is not None:
                    tasks.append(
                        create_task(self.__motor.set_speed(motor_speed))
                        )

                if servo_angle is not None:
                    tasks.append(
                        create_task(self.__servo.set_angle(servo_angle))
                        )

            # Gather the tasks and wait for them to complete
            await gather(*tasks) if tasks else None

        # Stop the serial communication when exiting the loop
        await self.__serial_communication.stop()


class WithObstacles:
    """
    Class for the WRO 2025 Challenge with Obstacles in the Future Engineers Car category.
    This class contains constants and methods related to the challenge.
    """

    def __init__(
        self,
        bno08x: BNO08XHandler,
        servo: ServoHandler,
        motor: ESCMotorHandler,
        serial_communication: SerialCommunication
        ):
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
