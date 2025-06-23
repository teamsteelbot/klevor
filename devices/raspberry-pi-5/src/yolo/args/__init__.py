from argparse import ArgumentParser

from ...constants import MODELS_NAME, SIZE
from .enums import Flag
from ...args import Args as A
from ..constants import FORMAT_PT, FORMATS


class Args(A):
    """
    Class to handle command line arguments.
    """

    @classmethod
    def add_yolo_input_model_pt_argument(cls, parser: ArgumentParser) -> None:
        """
        Add YOLO input PyTorch model argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
        """
        cls._add_non_boolean_argument(parser, Flag.INPUT_MODEL_PT, type=str, required=True,
                                      help='YOLO input PyTorch model',)

    @classmethod
    def add_yolo_output_model_argument(cls, parser: ArgumentParser) -> None:
        """
        Add YOLO output model argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
        """
        cls._add_non_boolean_argument(parser, Flag.OUTPUT_MODEL, type=str, required=True, help='YOLO output model',
                            choices=MODELS_NAME)

    @classmethod
    def add_yolo_format_argument(cls, parser: ArgumentParser, required: bool = False) -> None:
        """
        Add YOLO format argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to False.
        """
        cls._add_non_boolean_argument(parser, Flag.FORMAT, type=str, required=required, help='YOLO format',
                                     choices=FORMATS, default=FORMAT_PT)

    @classmethod
    def add_yolo_quantized_argument(cls, parser: ArgumentParser, default: bool = False) -> None:
        """
        Add YOLO quantized argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            default (bool): Default value for the quantized argument. Defaults to False.
        """
        cls._add_boolean_argument(parser, Flag.QUANTIZED, default=default)

    @classmethod
    def add_yolo_retraining_argument(cls, parser: ArgumentParser, default: bool = False) -> None:
        """
        Add YOLO retraining argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            default (bool): Default value for the retraining argument. Defaults to False.
        """
        cls._add_boolean_argument(parser, Flag.RETRAINING, default=default)

    @classmethod
    def add_yolo_classes_argument(cls, parser: ArgumentParser, required: bool = True) -> None:
        """
        Add YOLO classes argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        cls._add_non_boolean_argument(parser, Flag.CLASSES, type=str, required=required, help='YOLO classes',
                                      nargs="*")

    @classmethod
    def add_yolo_ignore_classes_argument(cls, parser: ArgumentParser, required: bool = True) -> None:
        """
        Add YOLO ignore classes argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        cls._add_non_boolean_argument(parser, Flag.IGNORE_CLASSES, type=str, required=required,
                                      help='YOLO ignore classes', nargs="*")

    @classmethod
    def add_yolo_epochs_argument(cls, parser: ArgumentParser, required: bool = True) -> None:
        """
        Add YOLO epochs argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        cls._add_non_boolean_argument(parser, Flag.EPOCHS, type=int, required=required,
                                      help='YOLO epochs', default=100)

    @classmethod
    def add_yolo_device_argument(cls, parser: ArgumentParser, required: bool = True) -> None:
        """
        Add YOLO device argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        cls._add_non_boolean_argument(parser, Flag.DEVICE, type=str, required=required,
                                      help='YOLO device', choices=['0', 'cpu', 'cuda'], default='0')

    @classmethod
    def add_yolo_image_size_argument(cls, parser: ArgumentParser, required: bool = True) -> None:
        """
        Add YOLO image size argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        cls._add_non_boolean_argument(parser, Flag.IMAGE_SIZE, type=int, required=required,
                                      help='YOLO image size', default=SIZE)

