from args import Args as A
from yolo import Yolo


class Args(A):
    """
    Class to handle command line arguments.
    """
    # Arguments
    DEBUG = 'debug'
    FORMAT = 'format'
    QUANTIZED = 'quantized'
    INPUT_MODEL = 'input-model'
    INPUT_MODEL_PT = 'input-model-pt'
    OUTPUT_MODEL = 'output-model'
    VERSION = 'version'
    RETRAINING = 'retraining'
    CLASSES = 'classes'
    IGNORE_CLASSES = 'ignore-classes'
    EPOCHS = 'epochs'
    DEVICE = 'device'
    IMAGE_SIZE = 'imgsz'

    @classmethod
    def add_yolo_input_model_argument(cls, parser) -> None:
        """
        Add YOLO input model argument to the parser.
        """
        parser.add_argument(cls.get_attribute_name(cls.INPUT_MODEL), type=str, required=True, help='YOLO input model',
                            choices=Yolo.MODELS_NAME)

    @classmethod
    def add_yolo_input_model_pt_argument(cls, parser) -> None:
        """
        Add YOLO input PyTorch model argument to the parser.
        """
        parser.add_argument(cls.get_attribute_name(cls.INPUT_MODEL_PT), type=str, required=True,
                            help='YOLO input PyTorch model')

    @classmethod
    def add_yolo_output_model_argument(cls, parser) -> None:
        """
        Add YOLO output model argument to the parser.
        """
        parser.add_argument(cls.get_attribute_name(cls.OUTPUT_MODEL), type=str, required=True, help='YOLO output model',
                            choices=Yolo.MODELS_NAME)

    @classmethod
    def add_yolo_format_argument(cls, parser, required: bool = False) -> None:
        """
        Add YOLO format argument to the parser.
        """
        parser.add_argument(cls.get_attribute_name(cls.FORMAT), type=str, required=required, help='YOLO format',
                            choices=Yolo.FORMATS, default=Yolo.FORMAT_PT)

    @classmethod
    def add_yolo_quantized_argument(cls, parser, default: bool = False) -> None:
        """
        Add YOLO quantized argument to the parser.
        """
        parser.add_argument(f"--no-{cls.QUANTIZED}", dest=cls.QUANTIZED, action="store_false", help="Disable quantized")
        parser.add_argument(f"--{cls.QUANTIZED}", dest=cls.QUANTIZED, action="store_true", help="Enable quantized")
        parser.set_defaults(**{cls.QUANTIZED: default})

    @classmethod
    def add_yolo_version_argument(cls, parser) -> None:
        """
        Add YOLO version argument to the parser.
        """
        parser.add_argument(cls.get_attribute_name(cls.VERSION), type=str, required=True, help='YOLO model version',
                            choices=Yolo.VERSIONS)

    @classmethod
    def add_yolo_retraining_argument(cls, parser, default: bool = False) -> None:
        """
        Add YOLO retraining argument to the parser.
        """
        parser.add_argument(f"--no-{cls.RETRAINING}", dest=cls.RETRAINING, action="store_false",
                            help="Set retraining flag as 'False'")
        parser.add_argument(f"--{cls.RETRAINING}", dest=cls.RETRAINING, action="store_true",
                            help="Set retraining flag as 'True'")
        parser.set_defaults(**{cls.RETRAINING: default})

    @classmethod
    def add_yolo_classes_argument(cls, parser, required: bool = True) -> None:
        """
        Add YOLO classes argument to the parser.
        """
        parser.add_argument(cls.get_attribute_name(cls.CLASSES), type=str, required=required, help='YOLO classes',
                            nargs="*")

    @classmethod
    def add_yolo_ignore_classes_argument(cls, parser, required: bool = True) -> None:
        """
        Add YOLO ignore classes argument to the parser.
        """
        parser.add_argument(cls.get_attribute_name(cls.IGNORE_CLASSES), type=str, required=required,
                            help='YOLO ignore classes', nargs="*")

    @classmethod
    def add_yolo_epochs_argument(cls, parser, required: bool = True) -> None:
        """
        Add YOLO epochs argument to the parser.
        """
        parser.add_argument(cls.get_attribute_name(cls.EPOCHS), type=int, required=required, help='YOLO epochs',
                            default=100)

    @classmethod
    def add_yolo_device_argument(cls, parser, required: bool = True) -> None:
        """
        Add YOLO device argument to the parser.
        """
        parser.add_argument(cls.get_attribute_name(cls.DEVICE), type=str, required=required, help='YOLO device',
                            default='0')

    @classmethod
    def add_yolo_image_size_argument(cls, parser, required: bool = True) -> None:
        """
        Add YOLO image size argument to the parser.
        """
        parser.add_argument(cls.get_attribute_name(cls.IMAGE_SIZE), type=int, required=required, help='YOLO image size',
                            default=640)

    @classmethod
    def add_debug_argument(cls, parser, default: bool = False) -> None:
        """
        Add debug argument to the parser.
        """
        parser.add_argument(f"--no-{cls.DEBUG}", dest=cls.DEBUG, action="store_false", help="Set debug flag as 'False'")
        parser.add_argument(f"--{cls.DEBUG}", dest=cls.DEBUG, action="store_true", help="Set debug flag as 'True'")
        parser.set_defaults(**{cls.DEBUG: default})
