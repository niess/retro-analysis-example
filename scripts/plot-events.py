#! /usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
import pickle
from typing import NamedTuple

import matplotlib.pyplot as plot
import numpy

from utils.containers import *
from utils.histogram import Selection


WAXMAN_BAHCALL_FACTOR = 2E-04 / 3.0 # Assuming 1 / 3 tau neutrinos,
                                    # in GeV / m^2 s sr.

def waxman_bahcall_flux(energy):
    """Waxman-Bahcall bound."""

    return WAXMAN_BAHCALL_FACTOR / energy**2 # in 1 / GeV m^2 s sr,
                                             # with energy in GeV.


def fluxify(path):
    """Apply primary flux to Monte Carlo events."""

    class Result(NamedTuple):
        neutrinos: Selection
        taus: Selection

    with open(path, "rb") as f:
        data = pickle.load(f)

    # Container for tau candidates, as a numpy.ndarray.
    dtype = [
        ("angle", "f8"),
        ("energy", "f8"),
        ("rate", "f8")
    ]
    taus = numpy.empty(len(data["events"]), dtype=dtype)

    # Container for neutrino candidates, as a numpy.ndarray.
    dtype = [
        ("energy", "f8"),
        ("rate", "f8")
    ]
    neutrinos = numpy.empty(data["n_neutrinos"], dtype=dtype)

    # Loop over data and fill tau statistics.
    generated_taus, offset = 0, 0
    for i, event in enumerate(data["events"]):
        # Update total statistics.
        generated_taus += event.statistics.tau_trials

        # Compute primaries flux.
        primaries_flux = waxman_bahcall_flux(event.primaries.energy)

        # Compute event rate.
        rates = event.primaries.weight * primaries_flux / \
            event.statistics.neutrino_trials # in Hz.

        # Fill tau data.
        tau = taus[i]
        tau["angle"] = event.tau.horizontal_coordinates[0]
        tau["energy"] = event.tau.energy
        tau["rate"] = sum(rates)

        # Fill neutrino data.
        n = event.primaries.size
        neutrino = neutrinos[offset:offset+n]
        neutrino["energy"] = event.primaries.energy
        neutrino["rate"] = rates

        # Update offset of neutrinos array.
        offset += n

    return Result(
        neutrinos = Selection(events = neutrinos, N = generated_taus),
        taus = Selection(events = taus, N = generated_taus),
    )


def plot_spectra(events):
    """Plot spectra of fluxified Monte Carlo events."""

    # Print total rate (per year)
    year = 365.25 * 24 * 60 * 60
    rate = events.taus.total_rate * year
    print(f"rate = {rate:.2f} events / year")

    # Average exposure to tau neutrinos.
    energy_min, energy_max = 1E+07, 1E+11
    I = WAXMAN_BAHCALL_FACTOR * (                   # Flux integral,
        1.0 / energy_min - 1.0 / energy_max) * year # in 1 / m^2 sr year.
    exposure = rate / I
    print(f"exposure = {exposure:.2E} m^2 s")

    # Compute PDF estimates (by histograming weighted data).
    tau_angle = events.taus.histogram("angle")
    tau_energy = events.taus.histogram("energy", transform="log")
    neutrino_energy = events.neutrinos.histogram("energy", transform="log")

    # Load matplotlib stylesheet.
    prefix = Path(__file__).parent
    plot.style.use(prefix / "paper.mplstyle")

    # Plot PDF estimates (i.e. differential rates).
    plot.figure()
    tau_energy.errorbar(fmt="ko", label=r"$\tau$")
    neutrino_energy.errorbar(fmt="ro", label=r"$\nu_\tau$")
    plot.xscale("log")
    plot.yscale("log")
    plot.xlabel("energy (GeV)")
    plot.ylabel(r"rate (GeV$^{-1}$s$^{-1}$)")
    plot.legend()
    plot.xlim(1E+07, 1E+11)
    plot.ylim(1E-21, 1E-14)

    plot.figure()
    tau_angle.errorbar(fmt="ko")
    plot.xlabel(r"$\theta$ (deg)")
    plot.ylabel(r"rate (deg$^{-1}$s$^{-1}$)")

    plot.show()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    # Apply flux model to Monte Carlo events.
    events = fluxify(args.path)

    # Plot some distributions.
    plot_spectra(events)
