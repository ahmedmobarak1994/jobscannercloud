"""Source plugins"""
from .greenhouse import GreenhouseSource
from .lever import LeverSource
from .ashby import AshbySource

SOURCE_REGISTRY = {
    "greenhouse": GreenhouseSource,
    "lever": LeverSource,
    "ashby": AshbySource,
}

__all__ = ['SOURCE_REGISTRY']

