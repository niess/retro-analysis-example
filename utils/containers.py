"""Some data formats related to Monte Carlo events."""
from typing import NamedTuple, Tuple

import numpy

__all__ = ["Event", "Origin", "Primaries", "Statistics", "TauAtDecay"]


class Event(NamedTuple):
    """Tau candidate event."""

    primaries: "Primaries"
    statistics: "Statistics"
    tag: str
    tau: "TauAtDecay"

    @classmethod
    def from_event(cls, event):
        return cls(
            primaries = Primaries.from_event(event),
            statistics= Statistics.from_event(event),
            tag = event["tag"],
            tau = TauAtDecay.from_event(event)
        )


class Origin(NamedTuple):
    """Local frame origin."""

    latitude: float # in deg
    longitude: float # in deg

    @classmethod
    def from_event(cls, event):
        return cls(*event["origin"])


class Primaries(NamedTuple):
    """Primary neutrino ancesters."""

    size: int
    weight: numpy.ndarray # GeV m^2 sr
    energy: numpy.ndarray # GeV
    generation_index: numpy.ndarray
    medium: numpy.ndarray
    local_coordinates: numpy.ndarray # (x, y, z) in GRAND frame, in m.
    geodetic_coordinates: numpy.ndarray # (latitude, longitude, height)

    @classmethod
    def from_event(cls, event):
        primaries = event["primaries"]
        args = [
            numpy.array([primary[i] for primary in primaries])
                for i in range(len(cls._fields) - 1)
        ]
        return cls(len(primaries), *args)


class Statistics(NamedTuple):
    """Monte Carlo statistics."""

    tau_trials: float
    neutrino_trials: float

    @classmethod
    def from_event(cls, event):
        return cls(*event["statistics"])


class TauAtDecay(NamedTuple):
    """Data describing a tau right before its decay."""

    generation_weight: float # GeV m^3 sr.
    energy: float # GeV.
    position: Tuple[float] # (x, y, z), in GRAND frame, in m.
    direction: Tuple[float] # (ux, uy, uz), in GRAND frame.
    geodetic_coordinates: Tuple[float] # (latitude, longitude, height).
    horizontal_coordinates: Tuple[float] # (azimuth, elevation).

    @classmethod
    def from_event(cls, event):
        return cls(*event["tau_at_decay"])
