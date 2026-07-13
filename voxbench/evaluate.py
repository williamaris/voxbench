import os
import sys
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
    required = True,
    help = "Output directory where to save the results."
)

args = parser.parse_args()

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
results = {}
metrics = ["pesq", "stoi", "si-snr", "si-sdr", "csig", "cbak", "covl"]

for metric in metrics:
    results[metric] = {"noisy": [], "processed": []}

def log_result(metric, noisy_score, processed_score):
    results[metric]['noisy'].append(noisy_score)
    results[metric]['processed'].append(processed_score)

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

for metric in metrics:
    print(f"{metric}: {np.mean(results[metric]['noisy'])}")

