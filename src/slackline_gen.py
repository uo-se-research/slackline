"""Generate multiple slackline configuration files, for running
a series of experiments with variations (e.g., sensitivity analysis for a variable).
Each experiment is saved as a settings file in the specified directory.

This file must be hacked to create variations ... there is no external language for specifying
how parameters are varied (yet).
TODO:  This could be combined with combinatorial test coverage generation (e.g., pairwise coverage)
"""

import mutation.settings

import argparse

def cli() -> object:
    """Command line interface"""
    parser = argparse.ArgumentParser("Generate a varying set of experiment parameters")
    parser.add_argument("--base", type=str, default="mutation/defaults.yaml",
                        desc="YAML file on which to base variations")
    parser.add_argument("--dest", type=str, default="/tmp/gramfuzz",
                        desc="Directory in which to generate experimental settings files")
    return parser.parse_args()

def vary(settings: mutation.settings.Settings) -> iter[mutation.settings.Settings]:
    """Hack this generator to vary parameters in the settings object"""
    for tactic in ["SimpleFrontier", "WeightedFrontier"]:
        pass

