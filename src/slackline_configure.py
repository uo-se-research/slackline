"""Configure from a combination of configuration files and command line.
This is to be called from a main program operating at the "src" level in treeline,
one directory up from here.
"""
import argparse
import inspect
import os
import pathlib

import yaml

from mutation.settings import Settings
import mutation.search

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# I cannot believe these gyrations are necessary to get oriented to
# the "src" directory or "mutation" subdirectory.
# Todo: Simpler orientation to project root directory
filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
default_settings = pathlib.Path(path).joinpath("defaults.yaml")


def configure() -> Settings:
    """Combines configuration files with command line arguments."""
    cli_args = cli()
    config = Settings()
    if cli_args.config is None:
        config.read_yaml(open(default_settings))
    else:
        config.read_yaml(cli_args.config)
    # Command line arguments override settings file
    for arg in ["app_name", "gram_name", "gram_file", "directory",
                "length", "tokens", "runs",
                "slack", "search", "seconds"]:
        if cli_args.__getattribute__(arg):
            config[arg] = cli_args.__getattribute__(arg)

    frontier_strategies = {
        "SimpleFrontier": mutation.search.SimpleFrontier,
        "WeightedFrontier": mutation.search.WeightedFrontier
    }
    config.substitute({"FRONTIER": frontier_strategies})
    return config


def cli() -> object:
    """Command line interface, including information for logging"""
    parser = argparse.ArgumentParser(description="Mutating and splicing derivation trees")
    parser.add_argument("--app_name", type=str,
                        help="Application name, e.g., graphviz")
    parser.add_argument("--gram_name", type=str,
                        help="Name of grammar (abbreviated)")
    parser.add_argument("--gram_file", type=str,
                        help="Path to file containing grammar")
    parser.add_argument("--directory", type=str,
                        help="Root directory for experiment results")
    parser.add_argument("--length", type=int,
                        help="Upper bound on generated sentence length")
    parser.add_argument("--seconds", type=int,
                        help="Timeout in seconds, default 3600 (60 minutes)")
    parser.add_argument("--tokens", help="Limit by token count",
                        action="store_true")
    parser.add_argument("--runs", type=int,
                        help="How many times we should run the same experiment?")
    parser.add_argument("--slack", help="Report experiment to Slack",
                        action="store_true")
    parser.add_argument("--search",
                        help="bfs (breadth-first) or mcw (monte-carlo weighted)",
                        choices = ["bfs", "mcw"])
    parser.add_argument("--config", help="Base configuration file",
                        type=argparse.FileType("r"))
    return parser.parse_args()

def class_representer(dumper, data) -> str:
    """Experimental: Translate frontier classes back to string designations"""
    if data is mutation.search.SimpleFrontier:
        return "SimpleFrontier"
    elif data is mutation.search.WeightedFrontier:
        return "WeightedFrontier"
    else:
        return f"Class {data}"



def main():
    """Dummy main to check the behavior of configuation"""
    config = configure()
    log.debug(f"config['FRONTIER'] is {config['FRONTIER']}, type {type(config['FRONTIER'])}")
    yaml.add_representer(type(config["FRONTIER"]), class_representer)
    print(config.dump_yaml())

if __name__ == "__main__":
    main()
