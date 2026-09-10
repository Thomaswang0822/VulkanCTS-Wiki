"""Static registries used by the Wiki-evidence-first lookup database builder."""

from .category_inputs import (
    CATEGORY_MUSTPASS_FILES,
    mustpass_root_for,
    package_prefix_for,
)
from .ownership_aliases import OWNERSHIP_ALIASES, OWNERSHIP_EXCLUSIONS

__all__ = [
    "CATEGORY_MUSTPASS_FILES",
    "mustpass_root_for",
    "package_prefix_for",
    "OWNERSHIP_ALIASES",
    "OWNERSHIP_EXCLUSIONS",
]
