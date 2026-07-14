# VoxBench

List available datasets:

```bash
python -m voxbench.list_datasets
```

Get a copy of a dataset:

```bash
python -m voxbench.get_dataset --dataset <dataset_name> --output <output_dir>
```

Benchmark processed audio:

```bash
python -m voxbench.evaluate --dataset <dataset_name> --input <processed_audio_dir> --output <results_dir>
```

Compile results into a table:

1. Create list file containing the name of the models and the path to their benchmark results. For example:

```bash
Model 1 : ~/model_1/voxbench/voicebank_demand/voxbench_results.json
Model 2 : ~/model_2/voxbench/voicebank_demand/voxbench_results.json
Model 3 : ~/model_3/voxbench/voicebank_demand/voxbench_results.json
```

2. Enter command in terminal:

```bash
python -m voxbench.compile_results --input <list_file> --format <markdown || latex || csv> (--precision <n_decimals>) (--omit_sd)
```