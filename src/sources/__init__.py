"""Source plugins"""
from .greenhouse import GreenhouseSource
from .lever import LeverSource
from .ashby import AshbySource
from .remotive import RemotiveSource
from .weworkremotely import WeWorkRemotelySource

SOURCE_REGISTRY = {
    "greenhouse": GreenhouseSource,
    "lever": LeverSource,
    "ashby": AshbySource,
    "remotive": RemotiveSource,
    "weworkremotely": WeWorkRemotelySource,
}

__all__ = ['SOURCE_REGISTRY']

