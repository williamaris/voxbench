import os
import sys
import json
import shutil
import argparse
import numpy as np
from tqdm import tqdm

import voxbench.metrics as m
import voxbench.utils as utils
from voxbench.datasets.dataset import DATASET_REGISTRY


# Argument parser
parser = argparse.ArgumentParser()

parser.add_argument(
    '-d',
    '--dataset',
    type = str,
    required = True,
    help = "Name of the dataset."
)

parser.add_argument(
    '-i',
    '--input',
    type = str,
    required = True,
    help = "Input directory containing processed audio."
)

parser.add_argument(
    '-o',
    '--output',
    type = str,
    required = False,
    help = "Output directory where to save the results."
)

args = parser.parse_args()

if args.output is None:
    args.output = os.path.join(args.input, "..", "voxbench", args.dataset)

# Instantiate dataset
args.dataset = args.dataset.strip()

if args.dataset not in DATASET_REGISTRY.keys():
    raise KeyError(f"No dataset named '{args.dataset}' registered.")

dataset_cls = DATASET_REGISTRY[args.dataset]
dataset = dataset_cls()

# Check input dir integrity
for f, _, _ in dataset:
    filepath = os.path.join(args.input, f)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} not found.")

# Preparing results dict
results = {"dataset": args.dataset}
metrics = ["pesq", "stoi", "si-snr", "si-sdr", "csig", "cbak", "covl"]

for metric in metrics:
    results[metric] = {"noisy": [], "processed": []}

def log_result(metric, noisy_score, processed_score):
    results[metric]['noisy'].append(noisy_score.tolist())
    results[metric]['processed'].append(processed_score.tolist())

# Main processing loop
for filename, xs_data, ss_data in tqdm(dataset, desc = "Benchmarking"):
    # Loading processed audio
    ys_data = utils.load_audio(os.path.join(args.input, filename))

    # Unpacking
    xs, xs_fs = xs_data
    ss, ss_fs = ss_data
    ys, ys_fs = ys_data

    fs = xs_fs

    # Computing metrics
    noisy_pesq = m.compute_pesq(xs, ss, fs)
    processed_pesq = m.compute_pesq(ys, ss, fs)

    log_result('pesq', noisy_pesq, processed_pesq)

    noisy_stoi = m.compute_stoi(xs, ss, fs)
    processed_stoi = m.compute_stoi(ys, ss, fs)

    log_result('stoi', noisy_stoi, processed_stoi)

    noisy_si_snr = m.compute_si_snr(xs, ss)
    processed_si_snr = m.compute_si_snr(ys, ss)

    log_result('si-snr', noisy_si_snr, processed_si_snr)

    noisy_si_sdr = m.compute_si_sdr(xs, ss)
    processed_si_sdr = m.compute_si_sdr(ys, ss)

    log_result('si-sdr', noisy_si_sdr, processed_si_sdr)

    noisy_csig, noisy_cbak, noisy_covl = m.compute_composite(xs, ss, fs)
    processed_csig, processed_cbak, processed_covl = m.compute_composite(ys, ss, fs)

    log_result('csig', noisy_csig, processed_csig)
    log_result('cbak', noisy_cbak, processed_cbak)
    log_result('covl', noisy_covl, processed_covl)

# Compiling final results
summary = "="*61
summary += "\n" +  f" BENCHMARK RESULTS FOR DATASET: {args.dataset}"
summary += "\n" + "="*61
summary += "\n" + f"| {'Metric':<10} | {'Noisy (Mean ± SD)':<20} | {'Processed (Mean ± SD)':<21} |"
summary += "\n" + f"|{'-'*12}|{'-'*22}|{'-'*23}|"

for metric in metrics:
    noisy_vals = np.array(results[metric]['noisy'])
    proc_vals = np.array(results[metric]['processed'])

    n_mean, n_std = np.mean(noisy_vals), np.std(noisy_vals)
    p_mean, p_std = np.mean(proc_vals), np.std(proc_vals)

    results[metric]["noisy_mean"] = float(n_mean)
    results[metric]["noisy_std"] = float(n_std)
    results[metric]["processed_mean"] = float(p_mean)
    results[metric]["processed_std"] = float(p_std)

    summary += "\n" + f"| {metric.upper():<10} | {n_mean:>6.4f} ± {n_std:<10.4f} | {p_mean:>9.4f} ± {p_std:<11.4f} |"

summary += "\n" + "="*61

print("\n" + summary)

# Saving results
if not os.path.exists(args.output):
    os.makedirs(args.output)

with open(os.path.join(args.output, 'voxbench_results.json'), 'w') as f:
    json.dump(results, f, indent = 4)

with open(os.path.join(args.output, 'voxbench_summary.txt'), 'w') as f:
    f.write(summary)
