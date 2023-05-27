__author__ = "Ziyad Alsaeed"
__email__ = "zalsaeed@cs.uoregon.edu"
__status__ = "Testing"

"""
A helper script to collect the cost of experiment(s) and save them
to an easy to process CSV file.

It is important to know that this could be expensive in terms of time. 
The script will run each input 3-times collecting all possible information. 
And if the majority of the inputs are timing out, then each run will spend
the timeout duration x 3. 

TODO: replace this script with the inputs name parser script.  
"""

import os
import argparse
from collections import defaultdict

import helpers as helper
from analysis.run_app import AppRunner


if __name__ == "__main__":

    # define arguments
    parser = argparse.ArgumentParser(description="Command line utility for afl-showmax bulk runner.")
    parser.add_argument("dir", type=str, help="The directory to the experiment(s) for which inputs to be ran.")
    parser.add_argument("target", type=str, help="Target-App binary file")

    # get arguments
    args = parser.parse_args()

    # init the app runner given the binary passed
    ar = AppRunner(args.target)  # the app runner will fail if the binary has any issue

    # check if we are doing it for a single experiment or multiple ones.
    if not os.path.isdir(args.dir):
        raise RuntimeError(f'The path given in dir "{args.dir}" is not a directory')
    single_expr = False
    if os.path.exists(args.dir + '/queue') or os.path.exists(args.dir + '/buffer')\
            or os.path.exists(args.dir + '/list'):
        expr_dir = [os.path.dirname(args.dir).split('/')[-1]]
        args.dir = os.path.join(os.path.dirname(os.path.dirname(args.dir)))  # parent dir
        single_expr = True
    else:
        # collect  all sub-dir names in a list (if any)
        sub_dir = [f.name for f in os.scandir(args.dir) if f.is_dir()]
        expr_dir = []  # expr sub-dir only
        for d in sub_dir:
            if os.path.exists(args.dir + f'/{d}' + '/queue') or os.path.exists(args.dir + f'/{d}' + '/buffer') \
                    or os.path.exists(args.dir + f'/{d}' + '/list'):
                expr_dir.append(d)
    if not expr_dir:
        raise RuntimeError(f"Could not find queue/buffer dir in {args.dir} or any of its sub-directories.")

    # Copy inputs into new dirs and files with fixed names without losing important information
    helper.prep_expr_for_showmax(args.dir, expr_dir)
    expr_dir = helper.get_expr_dirs(args.dir)

    for expr in expr_dir:

        with open(f'{args.dir}/{expr}/expr-info.txt', 'r') as file:
            expr_info = file.read().replace('\n', '')

        print(f'Collecting data for {expr_info} in file {expr} ...')
        report = defaultdict(list)

        # we can get the name of the tool from the expr_info, but do we need it?

        # get names of all files in queue/buffer
        inputs = [f.name for f in os.scandir(args.dir + f'/{expr}/inputs') if f.is_file()]

        for file_name in sorted(inputs):
            # collect data from the file name
            indicators = file_name.split(',')

            # collect and store the data from name
            for indicator in indicators:  # e.g. id:****, exec:****, ... etc
                broken_indicator = indicator.split(':')
                if len(broken_indicator) != 2:
                    raise RuntimeError(f'Unexpected file name pattern {broken_indicator}')
                indicator_id, indicator_val = broken_indicator
                report[indicator_id].append(indicator_val)

            # collect data from the file system stat (timestamp, size-bytes)
            report['mtime(seconds)'].append(os.path.getmtime(args.dir + f'/{expr}/inputs' + f'/{file_name}'))
            report['size(byte)'].append(os.path.getsize(args.dir + f'/{expr}/inputs' + f'/{file_name}'))

            # collect data by running the input (cost, hotspot, coverage)
            pl, hs, cov = ar.run_showmax(args.dir + f'/{expr}/inputs' + f'/{file_name}')
            report['cost'].append(pl)
            report['hotspot'].append(hs)
            report['coverage'].append(cov)

        # validate that headers have list of the same size
        base_array_size = len(report['id'])
        for k, v in report.items():
            if len(v) != base_array_size:
                raise \
                    RuntimeError(f'The key {k}, has {len(v)} items that does not match the base size {base_array_size}')

        helper.write_dict_to_csv(report, output_dir=f'{args.dir}', file_name=f'{expr_info}')
        # FIXME: remove all the expr dirs we just created.
