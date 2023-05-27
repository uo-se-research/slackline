__author__ = "Ziyad Alsaeed"
__email__ = "zalsaeed@cs.uoregon.edu"
__status__ = "Testing"

import collections
import os
import sys
import math
import datetime
import subprocess
from typing import List, Iterable, Callable

import pandas as pd
import numpy as np


def progress_bar(is_time_based: bool, start_time: datetime, iter_counter: int, num_rollouts: int,
                 max_reward: float, len_reward_weight: float,
                 total_allowed_iter: int, refresh_threshold: float = 0.0, tail_len: int = 0,
                 uniqueness_per: float = 0.0, num_expansions: int = 0, num_edges: int = 0, num_hot_nodes: int = 0):
    """A method to show the progress bar of the run based on it whether being based on time or number of iter.

    :param is_time_based: Is the run restricted based on time or number of executions.
    :param start_time: The time when the run started.
    :param iter_counter: The iteration number (i.e., execution count).
    :param num_rollouts: The number of rollouts so far.
    :param num_expansions: The number of expansions so far.
    :param num_edges: The number of edges so far.
    :param num_hot_nodes: The number of hot-nodes identified.
    :param max_reward: The cost reward scaling.
    :param refresh_threshold: The dynamic refresh threshold.
    :param uniqueness_per: The uniqueness percentage of  the observed costs.
    :param tail_len: The tail length.
    :param len_reward_weight: The weight of the input length in the reward.
    :param total_allowed_iter: The number of app executions allowed if an iter based.
    """
    sys.stdout.write('\r')
    if is_time_based:
        sys.stdout.write("Duration(m)= %.5f, iter #%.1f, rollouts=%.1f, expansions=%.1f, edges=%.1f, "
                         "hot-nodes=%.1f, rMax=%.1f, refresh-threshold=%.5f, uniquenessPRC=%.5f, "
                         "len(tail)=%.3f, rw=%.1f" %
                         ((datetime.datetime.now() - start_time).seconds / 60,
                          iter_counter,
                          num_rollouts,
                          num_expansions,
                          num_edges,
                          num_hot_nodes,
                          max_reward,
                          refresh_threshold,
                          uniqueness_per,
                          tail_len,
                          len_reward_weight
                          )
                         )
    else:
        sys.stdout.write("[%-50s] %.2f%%, iter #%.1f, rollouts=%.1f, expansions=%.1f, edges=%.1f, "
                         "hot-nodes=%.1f, rMax=%.1f, refresh-threshold=%.5f, uniquenessPRC=%.5f, "
                         "len(tail)=%.1f, rw=%.3f" %
                         ('=' * int(50 * iter_counter / (total_allowed_iter - 1)),
                          100 * iter_counter / (total_allowed_iter - 1),
                          iter_counter,
                          num_rollouts,
                          num_expansions,
                          num_edges,
                          num_hot_nodes,
                          max_reward,
                          refresh_threshold,
                          uniqueness_per,
                          tail_len,
                          len_reward_weight
                          )
                         )
    sys.stdout.flush()


def scale_to_range(x_value, x_max, x_min, range_a, range_b) -> float:
    """Given a value x in a known range (min-max), squish it between a new defined range a and b.

    :param x_value: tha value to scale.
    :param x_max: the maximum value in the range from where x is given.
    :param x_min: the minimum value in the range from where x is given.
    :param range_a: the minimum value of the new scale.
    :param range_b: the maximum value of the new scale.
    :return: A value scaled within the new range a and b.
    """
    return (range_b - range_a) * (x_value - x_min) / (x_max - x_min) + range_a


def write_dict_to_csv(data: dict, output_dir: str, file_name: str, comments: str = None):
    """A method that takes a dictionary and uses  its keys as headers for a CSV file.

    :param data: The data passed as a dictionary.
    :param output_dir: full directory to which the output file should be saved.
    :param file_name: The desired name for the generated file.
    :param comments: Whether to add a comment to the CSV file header or not.
    """
    project_root = f"{output_dir}{file_name}.csv"

    with open(project_root, "w") as e_file:
        if comments is not None:
            e_file.write("# " + comments + "\n")
        pd.DataFrame(data).to_csv(e_file, index=False)


def get_exploration_rate(current_episode: int, decay_rate: float, max_exploration_rate: float,
                         min_exploration_rate: float) -> float:
    """
    A simple method that calculate the exploration rate based on how advance we are in the search process (how many
    steps we took) and the other constraints given by the user at the beginning of the experiment.

    :param current_episode: A count of the steps the agent took so far.
    :param decay_rate: the decay rate of exploration as we step through the environment we are learning. In other
        words, the speed in which we transition from exploration to exploitation.
    :param max_exploration_rate: the max possible probability of exploration at the beginning of learning.
    :param min_exploration_rate: the min possible probability of exploration throughout the learning process.
    :return: a decimal representing the exploration rate.
    """
    return min_exploration_rate + (max_exploration_rate - min_exploration_rate) \
        * math.exp(-1. * current_episode * decay_rate)


def is_confident(values: List[float], k: float = 0.8) -> bool:
    """After normalization, compares all the values in a list to the max value. If all values (other than the max)
    are below threshold compared to normalized max, then we are confident. Otherwise, we are not.

    :param values: The list of values
    :param k: The confidence threshold.
    :return: Whether all values are below k compared to the max or not.
    """
    if not values:
        raise RuntimeError("The list is empty!")

    max_val = max(values)
    min_val = min(values)
    values.remove(max(values))  # remove the max from the list as we don't want to compare with self

    if not values:  # there was only one value in the list, thus we must be confident.
        return True

    # fixme: should we really return in this case?
    if max_val == max(values):  # the highest two values are the same, return fast
        return False

    confident = True
    for v in values:
        if (1.0 - normalize(v, max_val, min_val)) < k:  # the value 1.0 is the max value when normalized
            confident = False
    return confident


def normalize(val, max_val, min_val):
    """Min-Max normalization (https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization)).

    :param val: Value to be normalized.
    :param max_val: The maximum possible value in the dataset.
    :param min_val: The minimum possible value in the dataset.
    :return: A normalized value between 0 and 1.
    """
    if (max_val - min_val) == 0:
        return 0.0
    else:
        return (val - min_val) / (max_val - min_val)


def prep_expr_for_showmax(root_path: str, expr_dir: List[str]):
    """For each expr directory copy all the input using a pattern we defined that would guarantee fixed naming
    length in both the dir names and the inputs names without losing essential information about the input
    (e.g. timestamp(mtime), exec, id).

    :PerfFuzz inputs naming samples:
    .. code-block::

        id:004322,src:004072,op:havoc,rep:4,exec:00005455595,+max
        id:003935,src:003637+000498,op:splice,rep:4,exec:00004626249,+max
        id:002391,src:002000+002009,op:splice,rep:8,exec:00001751333,+cov,+max

    :TreeLine naming samples:
    .. code-block::

        id:000091,cost:0000016880,hs:0000008440,hnb:0,exec:00000000150,len:010,tu:010+max
        id:000054,cost:0000017920,hs:0000008960,hnb:0,exec:00000000015,len:010,tu:010+cost+max

    :Target naming patter for each input:
    .. code-block::

        id:{6-digit},exec:{11-digits}

    Also each dir of each experiment must be named as expt:{4-digit}. This information of the experiment itself that
    used to be saved in the name, should be saved in a file named "expr-info.txt". Users of this method will use
    that file to retrieve the experiment information.

    :param root_path: The root path where all the experiments are saved (we can look at mutliple ones)
    :param expr_dir: All the experiment directories that we want to process.
    """
    # TODO: read name given the new method for names
    if root_path.endswith('/'):  # remove the last backslash
        root_path = root_path[:-1]
    expr_id = 1
    for expr in sorted(expr_dir):
        if os.path.exists(root_path + f'/{expr}' + '/queue'):
            inputs_dir = 'queue'
            technique = 'tool:PerfFuzz'
        elif os.path.exists(root_path + f'/{expr}' + '/buffer'):
            inputs_dir = 'buffer'
            technique = 'tool:TreeLine'
        elif os.path.exists(root_path + f'/{expr}' + '/list'):
            inputs_dir = 'list'
            technique = 'tool:SlackLine'
        else:
            raise RuntimeError(f"Cannot find queue/buffer/list in {root_path}/{expr}")
        # inputs_dir = 'queue' if os.path.exists(root_path + f'/{expr}' + '/queue') else 'buffer'
        # technique = 'tool:PerfFuzz' if inputs_dir == 'queue' else 'tool:TreeLine'

        # create a dir for this expr and a nested dir for inputs at the same time
        try:
            os.makedirs(f"{root_path}/expr:{expr_id:04d}/inputs")
            print(f"Directory: '{root_path}/expr:{expr_id:04d}/inputs' created")
        except FileExistsError:
            print(f"Directory: '{root_path}/expr:{expr_id:04d}/inputs' already exists!")

        # save expr info to file "expr-info.txt":
        with open(f"{root_path}/expr:{expr_id:04d}/expr-info.txt", "w") as expr_info:
            expr_info.write(f'{technique}-{expr}')

        # get names of all files in queue/buffer
        inputs = [f.name for f in os.scandir(root_path + f'/{expr}' + f'/{inputs_dir}') if f.is_file()]

        # loop saved inputs to copy each one to the new destination given the same parts of the name we care about
        for file_name in inputs:

            input_id = None
            input_exec = None
            input_crtime = None
            input_dur = None

            # remove postfix (e.g., +max, +cov, or +cost)
            base_name = file_name
            base_name = remove_suffix(base_name)

            # break by indicators and their values
            if base_name.endswith(','):
                base_name = base_name[:-1]

            if technique == 'tool:SlackLine':
                indicators = base_name.split('-')
            else:
                indicators = base_name.split(',')

            # checking if we should skip an input because it is an orig
            skip_this_input = False
            for indicator in indicators:  # e.g. id:****, exec:****, ... etc
                broken_indicator = indicator.split(':')
                if len(broken_indicator) == 2:
                    indicator_id, indicator_val = broken_indicator
                    if indicator_id in ['orig']:
                        skip_this_input = True

            if skip_this_input:
                continue

            for indicator in indicators:  # e.g. id:****, exec:****, ... etc
                broken_indicator = indicator.split(':')
                if len(broken_indicator) == 2:
                    indicator_id, indicator_val = broken_indicator
                    if indicator_id == 'id':
                        input_id = int(indicator_val)
                    if indicator_id == 'exec':
                        input_exec = int(indicator_val)
                    if indicator_id == 'crtime':
                        input_crtime = int(indicator_val)
                    if indicator_id == 'dur':
                        input_dur = int(indicator_val)
            if input_id is None:
                raise RuntimeError(f'Failed passing the id of the input{file_name} in '
                                   f'{root_path}/{expr}/{inputs_dir}')

            if input_crtime is None or input_dur is None or input_exec is None:
                raise RuntimeError(f'Accepting new experiments only! {file_name} in '
                                   f'{root_path}/{expr}/{inputs_dir} did not have exec, crtime, or dur')

            # the flag -p is to preserve the file mtime timestamp
            subprocess.run(['cp', '-p', f'{root_path}/{expr}/{inputs_dir}/{file_name}',
                            f'{root_path}/expr:{expr_id:04d}/inputs/id:{input_id:06d},exec:{input_exec:011d},'
                            f'crtime:{input_crtime},dur:{input_dur:010d}'])
        expr_id += 1


def remove_suffix(file_name: str, possible_suffixes=('+max', '+cov', '+cost', '+quant')) -> str:
    """Helper function to remove the suffixes added to the input files names.

    :param file_name: The file name with the undesired suffix.
    :param possible_suffixes: The suffixes that we might encounter and would like  to remove.
    :return: The same file name without any of the suffixes given.
    """
    while file_name.endswith(possible_suffixes):
        for suffix in possible_suffixes:
            if file_name.endswith(suffix):
                file_name = file_name[:-len(suffix)]
    return file_name


def get_expr_dirs(root_dir: str) -> list:
    """Helper function to collect the experiments directories for post-processing.

    :param root_dir: The main directory where all the experiments are collected.
    :return: A list of all the valid experiments directories.
    """

    # collect  all sub-dir names in a list (if any)
    sub_dir = [f.name for f in os.scandir(root_dir) if f.is_dir()]

    expr_dir = []  # expr sub-dir only

    for dir_name in sub_dir:
        if str(dir_name).startswith("expr:"):
            expr_dir.append(dir_name)

    if not expr_dir:
        raise RuntimeError(f'No "expr:" directories in the root dir {root_dir}')
    return sorted(expr_dir)


def top_n(items: Iterable, n: int = 10, key: Callable = None) -> Iterable:
    """Get the top (max) n elements in an iterable.

    :param items: The set of items to evaluate.
    :param n: The number of items to return.
    :param key: A key criteria to evaluate.
    :return: An iterable of len n or less sorted based on the key if given.
    """
    iter_len = sum(1 for _ in items)
    if n >= iter_len:
        return items

    if key is None:
        var = sorted(items)[-n:]
    else:
        var = sorted(items, key=key)[-n:]
    return var


def get_prc_of_value_above_threshold(data: List[int], k: int) -> float:
    """Given a list of data points, find the percentage of values above or equal to a given threshold
    from the list. For example, if the list is [1,2,3,4,5] and k=3, then the return value is 0.6 (i.e., 60%).

    :param data: List of data points
    :param k: Threshold to compare against.
    :return: Percentage of instances larger or equal to `k` from `data`.
    """
    if data:
        x = sum(i >= k for i in data)  # num of values larger than or equal to k
        return x / len(data)
    else:
        return 0.0


def find_prc_of_val_greater_than(data: List[int], k: int) -> float:
    if data:
        x = sum(i >= k for i in data)  # num of values larger than or equal to k
        return x/len(data)
    else:
        return 0.0


def find_prc_uniq_values(data: List[int]) -> float:
    """A function to calculate the percentage of duplicate value in a list. For example, if data=[1,1,1,2] then the
    return value will be 0.5 (or 50%). That is out of the four element only 50% are unique.

    :param data: A list of numbers.
    :return:  The percentage of unique value to the number of element in the list.
    """
    if data:
        return len(np.unique(data)) / len(data)
    else:
        return 0.0  # special case


def save_input(generated_input: str, hnb: bool, hnm: bool, hnc: bool, hs: int, ac: int, tokens_used: int,
               output_dir: str, input_id: int, exec_count: int, cur_ms: int, dur: int):
    """Save input to file with an extensively descriptive name. Name are descriptive as they are used later on
    analysis.

    :param generated_input: The input to be saved.
    :param hnb: The value of has-new-bits (coverage).
    :param hnm: The value of has-new-max.
    :param hnc: The value of has new cost.
    :param hs: The hotspot exhibited by the given input.
    :param ac: The cost exhibited by the given input.
    :param tokens_used: The number of tokens used to find the given input.
    :param output_dir: The directory where the input should be saved.
    :param input_id: The input ID.
    :param exec_count: The execution cont by the time this input was found.
    :param cur_ms: The current time when the input was found in milliseconds.
    :param dur: The duration value when the input was found during the run.
    """
    # FIXME: return a boolean to confirm the input saved successfully or not.
    if not os.path.isdir(output_dir):
        raise IOError(f'{output_dir} is not a directory.')

    postfix = ""
    if hnb:  # not 0 (we don't care either 1 or 2)
        postfix += "+cov"
    if hnm:
        postfix += "+max"
    if hnc:
        postfix += "+cost"
    # TODO: change the len tracking to be based on the len given by the user (e.g., char, or byte).
    with open(f"{output_dir}id:{input_id:06d},cost:{ac:010d},hs:{hs:010d},hnb:{hnb},exec:{exec_count},"
              f"len:{len(bytes(generated_input, 'utf-8')):03d},tu:{tokens_used:03d},crtime:{cur_ms},"
              f"dur:{dur}{postfix}", "wb") as cov_file:
        cov_file.write(generated_input.encode())


def beautify_final_report(data: dict) -> str:
    """Beautify the final report for printing/saving.

    :param data: The final report as a dictionary.
    :return: The final report beautified as a string.
    """
    # FIXME: why not as json? Make this usable if needed.
    categorized_data = collections.defaultdict(list)
    for k, v in sorted(data.items()):
        group_key = str(k).split(":")[0]
        categorized_data[group_key].append(f"{k} = {v}")

    result = ""
    for key, value in categorized_data.items():
        result += f"{key}\n"
        result += "="*50 + "\n"
        for v in value:
            result += f"{v}\n"
        result += "\n"
    return result
