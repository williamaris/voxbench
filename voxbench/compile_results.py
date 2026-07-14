import os
import json
import argparse

# Argument parser
parser = argparse.ArgumentParser()

parser.add_argument(
    '-i',
    '--input',
    type = str,
    required = True,
    help = "Input file containing IDs \
    and paths to benchmark files to process."
)

parser.add_argument(
    '-f',
    '--format',
    choices = ["markdown", "latex", "csv"],
    required = True,
    help = "Output format of the table."
)

parser.add_argument(
    '-p',
    '--precision',
    type = int,
    required = False,
    default = 4,
    help = "Number of decimals."
)

parser.add_argument(
    '-s',
    '--omit_sd',
    action = 'store_true',
    help = "Omit standard deviations."
)

args = parser.parse_args()

# List benchmark files to process
benchmark_files = {}

with open(args.input, 'r') as f:
    for line in f:
        model, benchmark_file = line.strip().split(" : ")
        benchmark_files[model] = benchmark_file

# Processing files
results = {}

for model, benchmark_file in benchmark_files.items():
    # Load benchmark data
    with open(benchmark_file, 'r') as f:
        data = json.load(f)

    # Add unknown metrics
    for k in data.keys():
        if k == "dataset":
            continue

        if results.get(k) is None:
            results[k] = {}

    # Add results
    for k in data.keys():
        if k == "dataset":
            continue

        n_mean = data[k]["noisy_mean"]
        n_std = data[k]["noisy_std"]
        p_mean = data[k]["processed_mean"]
        p_std = data[k]["processed_std"]

        results[k]["noisy"] = f"{n_mean:0.4f}"

        if not args.omit_sd:
            results[k]["noisy"] += f" ± {n_std:0.4f}"

        results[k][model] = f"{p_mean:0.4f}"

        if not args.omit_sd:
            results[k][model] += f" ± {p_std:0.4f}"

# Generate table
metrics = list(results.keys())
rows = ["noisy"] + list(benchmark_files.keys())

if args.format == "markdown":
    raise NotImplementedError()

elif args.format == "latex":
    raise NotImplementedError()

elif args.format == "csv":
    raise NotImplementedError()