"""UK Copy Checker: a house style checker for UK English."""
from .checker import Config, check_path, check_text
from .rules import RULES, Issue

__version__ = "1.0.0"
__all__ = ["Config", "check_path", "check_text", "RULES", "Issue", "__version__"]
