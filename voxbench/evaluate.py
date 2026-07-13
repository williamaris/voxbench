from voxbench.datasets.voicebank_demand import VoiceBankDEMAND
from voxbench.datasets.dataset import DATASET_REGISTRY

dataset = VoiceBankDEMAND()

print(len(dataset))

filename, xs_data, ss_data = dataset[0]

print(filename)
print(xs_data[0].shape)
print(xs_data[1])

print(DATASET_REGISTRY)