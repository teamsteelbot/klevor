# Arguments
ARGS_PREFIX = '--'

def get_attribute_name(attribute: str) -> str:
    """
    Get the attribute name.
    """
    return f'{ARGS_PREFIX}{attribute}'

def get_attribute_from_args(args, attribute: str):
    """
    Get the attribute name from the args.
    """
    # Substitute whitespaces with underscores
    attribute = attribute.replace(' ', '_')

    # Substitute dashes with underscores
    attribute = attribute.replace('-', '_')

    return args[attribute]

def parse_args_as_dict(parser):
    """
    Parse the arguments and return them as a dictionary.
    """
    # Parse the arguments
    args = parser.parse_args()

    # Get the arguments as a dictionary
    return vars(args)