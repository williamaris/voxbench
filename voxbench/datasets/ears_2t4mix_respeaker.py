import os
import glob
import shutil
import zipfile
import huggingface_hub as hf
from concurrent.futures import ThreadPoolExecutor

import voxbench.utils as utils
from voxbench.datasets.dataset import Dataset, register_dataset


@register_dataset
class EARS2t4MixReSpeaker(Dataset):

    name = "ears_2t4mix_respeaker"

    def __init__(self):
        super().__init__(self.name)

    def _download(self):
        print("Downloading fresh dataset copy...\n---")

        os.environ["HF_XET_HIGH_PERFORMANCE"] = "0"

        hf.login()

        # Create output dir
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

        os.makedirs(self.root)

        full_reverb = utils.selection_prompt(
            prompt="Use samples with full reverb for clean speech?",
            options = ["Yes", "No"],
            default = 0
        )[0]

        single_channel = utils.selection_prompt(
            prompt="Use single channel audio for clean speech?",
            options = ["Yes", "No"],
            default = 0
        )[0]

        clean_speech_file = "clean"

        if full_reverb != "Yes":
            clean_speech_file += "_no_reverb"

        if single_channel != "Yes":
            clean_speech_file += "_4ch"

        clean_speech_file += ".zip"

        hf.snapshot_download(
            repo_id = "williamaris/ears_2t4mix_respeaker",
            repo_type = "dataset",
            local_dir = self.root,
            allow_patterns=[
                "metadata.zip",
                "noisy.zip",
                clean_speech_file
            ],
            max_workers = 8
        )

        print('\n'*2)

        logout = utils.selection_prompt(
            prompt = "Logout from HuggingFace Hub?",
            options = ["Yes", "No"],
            default = 0
        )[0]

        if logout == "Yes":
            hf.logout()

        zip_files = glob.glob(os.path.join(self.root, "**/*.zip"), recursive=True)

        for zip_file in zip_files:
            filename = os.path.basename(zip_file)
            print(f"Extracting {filename}...")

            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.root)

            os.remove(zip_file)

        old_clean_dir = os.path.join(self.root, clean_speech_file.replace(".zip", ""))
        new_clean_dir = os.path.join(self.root, "clean")

        if os.path.exists(old_clean_dir):
            os.rename(old_clean_dir, new_clean_dir)

        print('---')

        return True