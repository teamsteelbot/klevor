from argparse import ArgumentParser

from .enums import Flags
from ...args import Args as A
from .. import Yolo

class Args(A):
    """
    Class to handle command line arguments.
    """

    @classmethod
    def add_yolo_input_model_argument(cls, parser: ArgumentParser) -> None:
        """
        Add YOLO input model argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
        """
        cls._add_non_boolean_argument(parser, Flags.INPUT_MODEL, type=str, required=True, help='YOLO input model',
                            choices=Yolo.MODELS_NAME)

    @classmethod
    def add_yolo_input_model_pt_argument(cls, parser: ArgumentParser) -> None:
        """
        Add YOLO input PyTorch model argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
        """
        cls._add_non_boolean_argument(parser, Flags.INPUT_MODEL_PT, type=str, required=True,
                                      help='YOLO input PyTorch model',)

    @classmethod
    def add_yolo_output_model_argument(cls, parser: ArgumentParser) -> None:
        """
        Add YOLO output model argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
        """
        cls._add_non_boolean_argument(parser, Flags.OUTPUT_MODEL, type=str, required=True, help='YOLO output model',
                            choices=Yolo.MODELS_NAME)

    @classmethod
    def add_yolo_format_argument(cls, parser: ArgumentParser, required: bool = False) -> None:
        """
        Add YOLO format argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to False.
        """
        cls._add_non_boolean_argument(parser, Flags.FORMAT, type=str, required=required, help='YOLO format',
                                     choices=Yolo.FORMATS, default=Yolo.FORMAT_PT)

    @classmethod
    def add_yolo_quantized_argument(cls, parser: ArgumentParser, default: bool = False) -> None:
        """
        Add YOLO quantized argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            default (bool): Default value for the quantized argument. Defaults to False.
        """
        cls._add_boolean_argument(parser, Flags.QUANTIZED, default=default)

    @classmethod
    def add_yolo_version_argument(cls, parser: ArgumentParser) -> None:
        """
        Add YOLO version argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
        """
        cls._add_non_boolean_argument(parser, Flags.VERSION, type=str, required=True, help='YOLO model version',
                                      choices=Yolo.VERSIONS)

    @classmethod
    def add_yolo_retraining_argument(cls, parser: ArgumentParser, default: bool = False) -> None:
        """
        Add YOLO retraining argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            default (bool): Default value for the retraining argument. Defaults to False.
        """
        cls._add_boolean_argument(parser, Flags.RETRAINING, default=default)

    @classmethod
    def add_yolo_classes_argument(cls, parser: ArgumentParser, required: bool = True) -> None:
        """
        Add YOLO classes argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        cls._add_non_boolean_argument(parser, Flags.CLASSES, type=str, required=required, help='YOLO classes',
                                      nargs="*")

    @classmethod
    def add_yolo_ignore_classes_argument(cls, parser: ArgumentParser, required: bool = True) -> None:
        """
        Add YOLO ignore classes argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        cls._add_non_boolean_argument(parser, Flags.IGNORE_CLASSES, type=str, required=required,
                                      help='YOLO ignore classes', nargs="*")

    @classmethod
    def add_yolo_epochs_argument(cls, parser: ArgumentParser, required: bool = True) -> None:
        """
        Add YOLO epochs argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        cls._add_non_boolean_argument(parser, Flags.EPOCHS, type=int, required=required,
                                      help='YOLO epochs', default=100)

    @classmethod
    def add_yolo_device_argument(cls, parser: ArgumentParser, required: bool = True) -> None:
        """
        Add YOLO device argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        cls._add_non_boolean_argument(parser, Flags.DEVICE, type=str, required=required,
                                      help='YOLO device', choices=['0', 'cpu', 'cuda'], default='0')

    @classmethod
    def add_yolo_image_size_argument(cls, parser: ArgumentParser, required: bool = True) -> None:
        """
        Add YOLO image size argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        cls._add_non_boolean_argument(parser, Flags.IMAGE_SIZE, type=int, required=required,
                                      help='YOLO image size', default=640)

    @classmethod
    def add_debug_argument(cls, parser: ArgumentParser, default: bool = False) -> None:
        """
        Add debug argument to the parser.

        Args:
            parser (ArgumentParser): The argument parser to which the argument will be added.
            default (bool): Default value for the debug argument. Defaults to False.
        """
        cls._add_boolean_argument(parser, Flags.DEBUG, default=default)
