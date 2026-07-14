import os
import shutil
import huggingface_hub as hf

from voxbench.datasets.dataset import Dataset, register_dataset


@register_dataset
class EARS24MixReSpeaker(Dataset):

    name = "ears_24mix_respeaker"

    def __init__(self):
        super().__init__(self.name)

    def _download(self):
        print("Downloading fresh dataset copy...\n---")

        hf.login()

        # Create output dir
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

        os.makedirs(self.root)

        hf.snapshot_download(
            repo_id = "williamaris/ears_24mix_respeaker",
            repo_type = "dataset",
            local_dir = self.root
        )

        print('\n'*2)

        while True:
            choice = input("Do you want to logout from HuggingFace Hub? (Y/n): ")
            choice = choice.strip().lower()

            if choice in ['', 'y', 'yes']:
                hf.logout()
                break

            elif choice in ['n', 'no']:
                break

            else:
                print("Invalid input. Please entre 'y' or 'n'.")

        print('---')

        return True