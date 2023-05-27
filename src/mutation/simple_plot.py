"""A quick-and-dirty plot from an experiment log, WITHOUT running showmax
(i.e., plot of times and edge counts during search, subject to distortions
that we do not tolerate for experiment analysis).
This is for tuning tools, not for publishable data.
"""

import argparse
import collections
import pathlib
import re
from typing import NamedTuple

# Standard matplotlib, names as in tutorials
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def cli() -> object:
    """Command line interface currently has just one argument,
    the path to the directory containing a list of input files.
    """
    parser = argparse.ArgumentParser(
        prog="simple_plot",
        description="Quick and dirty plot of experiment results for tuning")
    parser.add_argument('path', type=pathlib.Path)
    args = parser.parse_args()
    return args


def glob_names(dir_path: pathlib.Path) -> list[str]:
    """Returns a list of file name stems
     of the expected pattern in the directory.
    """
    return [str(f.stem) for f in dir_path.glob("id:*crtime*dur*")]


class Attr(NamedTuple):
    """Attributes extracted from file name of a logged generated input"""
    cost: int
    dur: int
    virtue: str


AttrPat = re.compile(r"""
    id:.*
    cost:(?P<cost> [0-9]+).*
    dur:(?P<dur> [0-9]+).* 
    \+(?P<virtue> [a-z]+)$
    """, re.VERBOSE)


def attributes(name: str) -> Attr:
    """Convert string file name to named tuple of attributes"""
    match = AttrPat.match(name)
    assert match, f"Oops, string {name} didn't match"
    groups = match.groupdict()
    return Attr(int(groups["cost"]), int(groups["dur"]), groups["virtue"])


def attr_vecs(names: list[str]) -> dict[str, list]:
    """Extract attributes into parallel numpy arrays in a dict,
    more compatible with numpy and matplotlib.
    Dict fields correspond to fields of Attr namedtuple.
    """
    costs: list[int] = []
    elapsed: list[float] = []
    virtues: list[str] = []
    for name in names:
        attr = attributes(name)
        costs.append(attr.cost)
        elapsed.append(round(attr.dur/1000, 2))
        virtues.append(attr.virtue)
    return {"cost": np.array(costs),
            "elapsed": np.array(elapsed),
            "virtue": np.array(virtues)}


def main():
    args = cli()
    dir_path = args.path
    print(f"Searching {dir_path}")
    names = glob_names(dir_path)
    print(f"{len(names)} files")
    frame = attr_vecs(names)
    print(f"{len(frame['elapsed'])} entries")
    fig, ax = plt.subplots()
    ax.scatter(frame["elapsed"], frame["cost"])
    fig.show()
    prompt = input("Ready?")
    print("Plotted!")


if __name__ == "__main__":
    main()
