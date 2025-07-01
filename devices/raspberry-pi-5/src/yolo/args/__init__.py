from typing import List

from .enums import Flag
from ..constants import FORMATS, FORMAT_PT
from ...args import Args as A
from ...constants import MODELS_NAME, SIZE


class Args(A):
    """
    Class to handle command line arguments.
    """

    def add_yolo_input_model_pt_argument(self) -> None:
        """
        Add YOLO input PyTorch model argument to the parser.
        """
        self._add_non_boolean_argument(
            Flag.INPUT_MODEL_PT,
            type=str,
            required=True,
            help='YOLO input PyTorch model',
        )

    def get_yolo_input_model_pt(self) -> str:
        """
        Get the YOLO input PyTorch model argument.

        Returns:
            str: The YOLO input PyTorch model.
        """
        return self._get_attribute_from_args_dict(Flag.INPUT_MODEL_PT)

    def add_yolo_output_model_argument(self) -> None:
        """
        Add YOLO output model argument to the parser.
        """
        self._add_non_boolean_argument(
            Flag.OUTPUT_MODEL,
            type=str,
            required=True, help='YOLO output model',
            choices=MODELS_NAME
        )

    def get_yolo_output_model(self) -> str:
        """
        Get the YOLO output model argument.

        Returns:
            str: The YOLO output model.
        """
        return self._get_attribute_from_args_dict(Flag.OUTPUT_MODEL)

    def add_yolo_format_argument(
        self,
        required: bool = False
    ) -> None:
        """
        Add YOLO format argument to the parser.

        Args:
            required (bool): Whether the argument is required or not. Defaults to False.
        """
        self._add_non_boolean_argument(
            Flag.FORMAT,
            type=str,
            required=required,
            help='YOLO format',
            choices=FORMATS,
            default=FORMAT_PT
        )

    def get_yolo_format(self) -> str:
        """
        Get the YOLO format argument.

        Returns:
            str: The YOLO format.
        """
        return self._get_attribute_from_args_dict(Flag.FORMAT)

    def add_yolo_quantized_argument(
        self,
        default: bool = False
    ) -> None:
        """
        Add YOLO quantized argument to the parser.

        Args:
            default (bool): Default value for the quantized argument. Defaults to False.
        """
        self._add_boolean_argument(Flag.QUANTIZED, default=default)

    def get_yolo_quantized(self) -> bool:
        """
        Get the YOLO quantized argument.

        Returns:
            bool: The YOLO quantized flag.
        """
        return self._get_attribute_from_args_dict(Flag.QUANTIZED)

    def add_yolo_retraining_argument(
        self,
        default: bool = False
    ) -> None:
        """
        Add YOLO retraining argument to the parser.

        Args:
            default (bool): Default value for the retraining argument. Defaults to False.
        """
        self._add_boolean_argument(Flag.RETRAINING, default=default)

    def get_yolo_retraining(self) -> bool:
        """
        Get the YOLO retraining argument.

        Returns:
            bool: The YOLO retraining flag.
        """
        return self._get_attribute_from_args_dict(Flag.RETRAINING)

    def add_yolo_classes_argument(
        self,
        required: bool = True
    ) -> None:
        """
        Add YOLO classes argument to the parser.

        Args:
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        self._add_non_boolean_argument(
            Flag.CLASSES,
            type=str,
            required=required,
            help='YOLO classes',
            nargs="*"
        )

    def get_yolo_classes(self) -> List[str]:
        """
        Get the YOLO classes argument.

        Returns:
            List[str]: The YOLO classes.
        """
        return self._get_attribute_from_args_dict(Flag.CLASSES)

    def add_yolo_ignore_classes_argument(
        self,
        required: bool = True
    ) -> None:
        """
        Add YOLO ignore classes argument to the parser.

        Args:
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        self._add_non_boolean_argument(
            Flag.IGNORE_CLASSES,
            type=str,
            required=required,
            help='YOLO ignore classes',
            nargs="*"
        )

    def get_yolo_ignore_classes(self) -> List[str]:
        """
        Get the YOLO ignore classes argument.

        Returns:
            List[str]: The YOLO ignore classes.
        """
        return self._get_attribute_from_args_dict(Flag.IGNORE_CLASSES)

    def add_yolo_epochs_argument(
        self,
        required: bool = True
    ) -> None:
        """
        Add YOLO epochs argument to the parser.

        Args:
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        self._add_non_boolean_argument(
            Flag.EPOCHS,
            type=int,
            required=required,
            help='YOLO epochs',
            default=100
        )

    def get_yolo_epochs(self) -> int:
        """
        Get the YOLO epochs argument.

        Returns:
            int: The number of YOLO epochs.
        """
        return self._get_attribute_from_args_dict(Flag.EPOCHS)

    def add_yolo_device_argument(
        self,
        required: bool = True
    ) -> None:
        """
        Add YOLO device argument to the parser.

        Args:
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        self._add_non_boolean_argument(
            Flag.DEVICE,
            type=str,
            required=required,
            help='YOLO device',
            choices=['0', 'cpu', 'cuda'],
            default='0'
        )

    def get_yolo_device(self) -> str:
        """
        Get the YOLO device argument.

        Returns:
            str: The YOLO device.
        """
        return self._get_attribute_from_args_dict(Flag.DEVICE)

    def add_yolo_image_size_argument(
        self,
        required: bool = True
    ) -> None:
        """
        Add YOLO image size argument to the parser.

        Args:
            required (bool): Whether the argument is required or not. Defaults to True.
        """
        self._add_non_boolean_argument(
            Flag.IMAGE_SIZE,
            type=int,
            required=required,
            help='YOLO image size',
            default=SIZE
        )

    def get_yolo_image_size(self) -> int:
        """
        Get the YOLO image size argument.

        Returns:
            int: The YOLO image size.
        """
        return self._get_attribute_from_args_dict(Flag.IMAGE_SIZE)
