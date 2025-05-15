from args import ARGS_PREFIX


# Get the attribute name
def get_attribute_name(attribute: str) -> str:
    return f'{ARGS_PREFIX}{attribute}'

# Get the attribute name from the args
def get_attribute_from_args(args, attribute: str) -> str:
    # Substitute whitespaces with underscores
    attribute = attribute.replace(' ', '_')

    # Substitute dashes with underscores
    attribute = attribute.replace('-', '_')

    return getattr(args, attribute)
