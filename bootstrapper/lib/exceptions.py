class RequiredParametersError(ValueError):
    """Custom error to denote when the proper parameters are not present"""


class TemplateNotFoundError(Exception):
    """Custom error to denote when a template is not found"""


class InvalidConfigurationError(Exception):
    """Custom error to denote when a template is not found"""
