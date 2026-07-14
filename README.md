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

```bash
python -m voxbench.compile_results --input <list_file> --format <markdown || latex || csv> (--omit_sd)
```