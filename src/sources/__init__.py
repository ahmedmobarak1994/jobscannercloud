"""Source plugins"""
from .greenhouse import GreenhouseSource
from .lever import LeverSource
from .ashby import AshbySource
from .remotive import RemotiveSource
from .weworkremotely import WeWorkRemotelySource
from .adzuna import AdzunaSource
from .remoteok import RemoteOKSource

SOURCE_REGISTRY = {
    "greenhouse": GreenhouseSource,
    "lever": LeverSource,
    "ashby": AshbySource,
    "remotive": RemotiveSource,
    "weworkremotely": WeWorkRemotelySource,
    "adzuna": AdzunaSource,
    "remoteok": RemoteOKSource,
}

__all__ = ['SOURCE_REGISTRY']

