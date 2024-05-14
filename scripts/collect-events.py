#! /usr/bin/env python3
from argparse import ArgumentParser
import glob
import json
from pathlib import Path
import pickle
from typing import NamedTuple

from utils.containers import *


def process_voltage_file(path):
    """Process a voltage file."""

    class Result(NamedTuple):
        event: Event
        origin: Origin

    with open(path) as f:
        for line in f:
            event = json.loads(line)

            return Result(
                event = Event.from_event(event),
                origin = Origin.from_event(event)
            )


def process_batch(args):
    """Process a set of Monte Carlo voltage files."""

    voltage_files = glob.glob(f"{args.path}/*.voltage.json")
    n = len(voltage_files)
    print(f"found {n} voltage files")

    events, n_neutrinos = [], 0
    for i, path in enumerate(voltage_files):
        print(f"processing {i + 1} / {n}")
        result = process_voltage_file(path)

        if i == 0:
            origin = result.origin
        else:
            assert(result.origin == origin)

        events.append(result.event)
        n_neutrinos += result.event.primaries.size

    data = {
        "events": events,
        "n_neutrinos": n_neutrinos,
        "origin": origin
    }

    output = args.output or "events.pkl"
    output = Path(output)
    if not output.parent.exists():
        output.parent.mkdir()

    with output.open("wb") as f:
        pickle.dump(data, f)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()

    process_batch(args)
