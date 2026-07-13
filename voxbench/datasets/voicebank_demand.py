import os
import shutil

from voxbench.datasets.dataset import Dataset, register_dataset


@register_dataset
class VoiceBankDEMAND(Dataset):

    name = "voicebank_demand"

    def __init__(self):
        super().__init__(self.name)

    def _download(self):
        print("Downloading fresh dataset copy...\n---")

        # Create output dir
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

        os.makedirs(self.root)

        # Download noisy audio
        noisy_testset_url = "https://datashare.ed.ac.uk/bitstreams/13c1bfbf-14a6-41db-9b41-8f7310f01ad5/download"
        self._download_zip(noisy_testset_url, "noisy audio", "noisy")

        # Download clean audio
        clean_testset_url = "https://datashare.ed.ac.uk/bitstreams/dec213d3-bf57-4777-9663-c24bdce92d5e/download"
        self._download_zip(clean_testset_url, "clean audio", "clean")

        print('---')

        return True