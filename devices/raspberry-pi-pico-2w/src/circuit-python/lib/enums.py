class IncomingCategory:
    """
    Class to represent the enum categories of incoming messages from the Raspberry Pi 5.
    """
    STATUS = "status"
    MOTOR_SPEED = "motor_speed"
    SERVO_ANGLE = "servo_angle"

    @classmethod
    def from_string(cls, category_str: str) -> str:
        """
        Convert a string to a IncomingCategory enum value.

        Args:
            category_str (str): The string representation of the category.

        Returns:
            str: The corresponding IncomingCategory enum value.
        """
        category_name = category_str.lower()
        for category in [cls.STATUS, cls.MOTOR_SPEED, cls.SERVO_ANGLE]:
            if category_name == category:
                return category

        raise ValueError(f"Invalid incoming category: {category_str}")


class OutgoingCategory:
    """
    Class to represent the enum categories of outgoing messages to the Raspberry Pi 5.
    """
    CHALLENGE = "challenge"
    STATUS = "status"
    BNO08X_YAW = "bno08x_yaw"
    BNO08X_TURNS = "bno08x_turns"
    ERROR = "error"

    @classmethod
    def from_string(cls, category_str: str) -> str:
        """
        Convert a string to a OutgoingCategory enum value.

        Args:
            category_str (str): The string representation of the category.

        Returns:
            str: The corresponding OutgoingCategory enum value.
        """
        category_name = category_str.lower()
        for category in [cls.CHALLENGE, cls.STATUS, cls.BNO08X_YAW,
                         cls.BNO08X_TURNS, cls.ERROR]:
            if category_name == category:
                return category

        raise ValueError(f"Invalid outgoing category: {category_str}")


class Status:
    """
    Class to represent the enum status messages sent and received to the Raspberry Pi 5.
    """
    START = "start"
    STOP = "stop"
    OK = "ok"

    @classmethod
    def from_string(cls, status_str: str) -> str:
        """
        Convert a string to a Status enum value.

        Args:
            status_str (str): The string representation of the status.

        Returns:
            str: The corresponding Status enum value.
        """
        status_name = status_str.lower()
        for status in [cls.START, cls.STOP, cls.OK]:
            if status_name == status:
                return status

        raise ValueError(f"Invalid status: {status_str}")


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
        challenge_name = challenge_str.lower()
        for challenge in [cls.WITH_OBSTACLES, cls.WITHOUT_OBSTACLES]:
            if challenge_name == challenge:
                return challenge

        raise ValueError(f"Invalid challenge: {challenge_str}")
