"""Data types related to histograming."""
from typing import NamedTuple

import matplotlib.pyplot as plot
import numpy


class WeightedHistogram(NamedTuple):
    """Weighted histogram of a Monte Carlo property."""

    x: numpy.ndarray
    y: numpy.ndarray
    xerr: numpy.ndarray
    yerr: numpy.ndarray

    def errorbar(self, axis=None, **kwargs):
        """Errorbar plot."""

        if axis is None:
            axis = plot.gca()

        return axis.errorbar(
            self.x,
            self.y,
            xerr = self.xerr,
            yerr = self.yerr,
            **kwargs
        )


class Selection(NamedTuple):
    """Selection of Monte Carlo events."""

    events: numpy.ndarray
    N: int

    @property
    def total_rate(self):
        """Total rate for selected events."""

        return sum(self.events["rate"]) / self.N

    def histogram(self, attr, bins=None, transform=None):
        """Histogram the given attribute."""

        # Default settings.
        if bins is None:
            bins = 40

        if transform is None:
            transform = "uniform"

        # Aliases.
        samples = self.events[attr]
        w = self.events["rate"]

        # Set x-grid.
        if transform == "uniform":
            bins = numpy.linspace(min(samples), max(samples), bins)
            x = 0.5 * (bins[1:] + bins[:-1])
        elif transform == "log":
            bins = numpy.geomspace(min(samples), max(samples), bins)
            x = numpy.sqrt(bins[1:] * bins[:-1])
        else:
            raise ValueError(f"bad transform ({transform})")

        # Bin samples.
        s1, _ = numpy.histogram(samples, bins, weights=w)
        s2, _ = numpy.histogram(samples, bins, weights=w**2)

        # PDF estimate and corresponding error.
        width = bins[1:] - bins[:-1]
        nrm = 1.0 / (self.N * width)
        y = s1 * nrm
        yerr = numpy.sqrt(s2 - s1**2 / self.N) * nrm

        return WeightedHistogram(
            x = x,
            y = y,
            xerr = numpy.array([x - bins[:-1], bins[1:] - x]),
            yerr = yerr
        )
