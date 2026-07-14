from voxbench.datasets.dataset import DATASET_REGISTRY

print("\nAVAILABLE DATASETS")
print("=" * 25)

for d in DATASET_REGISTRY.keys():
    print(f"* {d}")

print("")