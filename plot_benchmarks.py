import matplotlib.pyplot as plt
import argparse
import json
import re
from collections import defaultdict

TIME_MULTIPLIERS = {"ns": 1, "us": 1e3, "ms": 1e6, "s": 1e9}


def read_info(fname, regex, time_name):
    regex = re.compile(regex)
    with open(fname, "r") as f:
        json_data = json.load(f)
    data = {"names": [], "time": []}
    for b_mark in json_data["benchmarks"]:
        if regex.search(b_mark["name"]):
            data["names"].append(b_mark["name"])
            data["time"].append(
                    b_mark[time_name] * TIME_MULTIPLIERS[b_mark["time_unit"]])
    return data


def setup_parser(parser):
    parser.add_argument('-i', "--input", default="results.json", type=str,
                        help="input json file with results")
    parser.add_argument("--norm", action="store_true", default=False,
                        help="Sets whether graph should be plotted using "
                        "normalized times or not")
    parser.add_argument("--time_name", action="store", default="cpu_time",
                        choices=["cpu_time", "real_time"],
                        help="Indicates which time column will be used for plotting graphs")
    parser.add_argument("--figsize", action="store", type=str, default="7 4",
                        help="Setting resulting figure size")
    parser.add_argument("--filter", action="store", default=".*", type=str,
                        help="Python regex for filtering which data to plot")
    parser.add_argument("--log", action="store_true", default=False,
                        help="Sets the time axis scale to be logarithmic")
    parser.add_argument("--separate", action="store_true", default=False,
                        help="If true for each group of input parameters "
                        "separate picture will be created")


def normalize_times(time_list):
    min_val = min(time_list)
    for i in range(len(time_list)):
        time_list[i] /= min_val


def get_group_name(name, index):
    # Here we can take only suffix, since in check_separate we have already
    # checked that prefix for all values is the same
    return name.split('/')[index]


def check_separate_groups(data, idx):
    groups = set()
    for bench_name in data["names"]:
        groups.add(get_group_name(bench_name, idx))
    return len(groups) > 1


def find_separating_index(data):
    min_slash_num = min([name.count('/') for name in data["names"]])
    for idx in range(0, min_slash_num+1):
        if check_separate_groups(data, idx):
            break
    return idx


def group_data(data, group_name_getter):
    sep_idx = find_separating_index(data)
    result = defaultdict(lambda: defaultdict(list))
    for name, time in zip(data["names"], data["time"]):
        group_name = group_name_getter(name, sep_idx)
        result[group_name]["names"].append(name)
        result[group_name]["time"].append(time)
    return result


def plot_data_general(data, args):
    time_unit = "ns"
    if args.norm:
        normalize_times(data["time"])
        time_unit = "a.u."
    groups = group_data(data, get_group_name)
    plt.figure(figsize=[int(val) for val in args.figsize.split()])
    plt.grid(zorder=0)
    for key, val in groups.items():
        plt.barh(val["names"], val["time"], zorder=3)
    plt.xlabel(f"time, {time_unit}")
    if(args.log):
        plt.xscale("log")
    plt.tight_layout()
    plt.show()


def get_case_parameters(benchmark_full_name, sep_index):
    count = 0
    for i, el in enumerate(benchmark_full_name):
        if el == "/":
            count += 1
        if count == sep_index + 1:
            break
    return benchmark_full_name[i:]


def plot_data_separate(data, args):
    time_unit = "ns"
    groups = group_data(data, get_case_parameters)
    for key, val in groups.items():
        if args.norm:
            normalize_times(val["time"])
            time_unit = "a.u."
        plt.figure(figsize=[int(val) for val in args.figsize.split()])
        plt.grid(zorder=0)
        for name, t in zip(val["names"], val["time"]):
            plt.barh(name, t, zorder=3)
        plt.xlabel(f"time, {time_unit}")
        if(args.log):
            plt.xscale("log")
        plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="Benchmark results plotter",
            description="Tool for selective plotting benchmark results from"
            " json file",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )
    setup_parser(parser)
    args = parser.parse_args()
    data = read_info(args.input, args.filter, args.time_name)
    if args.separate:
        plot_data_separate(data, args)
    else:
        plot_data_general(data, args)
