# Arguments
ARGS_PREFIX = '--'

# Get the attribute name
def get_attribute_name(attribute: str) -> str:
    return f'{ARGS_PREFIX}{attribute}'

# Get the attribute name from the args
def get_attribute_from_args(args, attribute: str):
    # Substitute whitespaces with underscores
    attribute = attribute.replace(' ', '_')

    # Substitute dashes with underscores
    attribute = attribute.replace('-', '_')

    return args[attribute]

# Parse the arguments and return them as a dictionary
def parse_args_as_dict(parser):
    # Parse the arguments
    args = parser.parse_args()

    # Get the arguments as a dictionary
    return vars(args)