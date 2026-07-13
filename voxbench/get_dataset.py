import os
import sys
import shutil
import argparse

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
    '-o',
    '--output',
    type = str,
    required = True,
    help = "Output directory where the dataset will be copied to."
)

args = parser.parse_args()

# Instantiate datatset
args.dataset = args.dataset.strip()

if args.dataset not in DATASET_REGISTRY.keys():
    raise KeyError(f"No dataset named '{args.dataset}' registered.")

dataset_cls = DATASET_REGISTRY[args.dataset]
dataset = dataset_cls()

# Check output path
output_path = os.path.join(args.output, args.dataset)

if os.path.exists(output_path):
    while True:
        choice = input(f"{output_path} already exists, overwrite it? (Y/n): ")
        choice = choice.strip().lower()

        if choice in ['', 'y', 'yes']:
            break

        elif choice in ['n', 'no']:
            sys.exit(1)

        else:
            print("Invalid input. Please entre 'y' or 'n'.")

    shutil.rmtree(output_path)

dataset.export(output_path)
print("---\nTask complete!")
