import os
import shutil
import zipfile
import requests
from tqdm import tqdm
from pathlib import Path

import voxbench.utils as utils
from voxbench.cache_manager import get_cache_manager

DATASET_REGISTRY = {}


class Dataset:
    def __init__(self, name):
        # Dataset identification
        self.name = name

        self.root = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                '..',
                'datasets',
                name
            )
        )

        # Check dataset integrity
        valid_dataset = self._validate_integrity()

        if not valid_dataset:
            if self._download():
                cache_manager = get_cache_manager()

                dataset_hash = cache_manager.hash_path(self.root)
                cache_manager.set_hash(self.name, dataset_hash)

            else:
                raise RuntimeError("Download failed.")

        # Clean and noisy dirs
        self.clean_dir = os.path.join(self.root, "clean")
        self.noisy_dir = os.path.join(self.root, "noisy")

        # Listing files
        self.filenames = []
        clean_dir = Path(self.clean_dir)

        for file in clean_dir.rglob("*"):
            if file.is_file():
                self.filenames.append(str(file.relative_to(clean_dir)))

        self.filenames.sort()

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        filename = self.filenames[idx]

        xs_data = utils.load_audio(os.path.join(self.noisy_dir, filename))
        ss_data = utils.load_audio(os.path.join(self.clean_dir, filename))

        return filename, xs_data, ss_data

    def export(self, dest_path):
        if (os.path.abspath(self.root) != os.path.abspath(dest_path)):
            print(f"Exporting dataset to: {dest_path}...")
            shutil.copytree(self.root, dest_path)

    def _validate_integrity(self):
        if not os.path.exists(self.root):
            print("Missing root.")
            return False

        cache_manager = get_cache_manager()
        stored_hash = cache_manager.get_hash(self.name)

        if stored_hash is None:
            print("Corrupt cache, can't validate dataset.")
            return False

        current_hash = cache_manager.hash_path(self.root)

        if stored_hash != current_hash:
            print("Corrupt dataset.")
            return False

        return True

    def _download_zip(self, url, desc, name = None):
        if os.path.exists("tmp.zip"):
            os.remove("tmp.zip")

        r = requests.get(url, stream = True)

        chunk_size = 1024 * 1024
        total_size = r.headers.get("Content-Length", 0)

        with open("tmp.zip", "wb") as f:
            with tqdm(
                desc=f"Downloading {desc}",
                total=int(total_size) if total_size else None,
                unit="B",
                unit_scale=True,
                unit_divisor=1024
            ) as pbar:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

        with zipfile.ZipFile("tmp.zip") as z:
            z.extractall("tmp")

        original_name = os.listdir("tmp")[0]
        if name is None: name = original_name

        shutil.move(
            os.path.join("tmp", original_name),
            os.path.join(self.root, name)
        )

        os.remove("tmp.zip")
        shutil.rmtree("tmp")

    def _download(self):
        raise NotImplementedError()


def register_dataset(cls):
    if not issubclass(cls, Dataset):
        raise TypeError("Only classes inheriting from Dataset can be registered.")

    if not hasattr(cls, "name") or cls.name is None:
        raise AttributeError(f"Class '{cls.__name__}' must define a unique name.")

    if cls.name in DATASET_REGISTRY:
        raise KeyError(f"Dataset with name '{cls.name}' already registered.")

    DATASET_REGISTRY[cls.name] = cls

    return cls