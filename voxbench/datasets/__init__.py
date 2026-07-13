import importlib
import pkgutil
from pathlib import Path

__all__ = []

for _, module_name, _ in pkgutil.iter_modules([str(Path(__file__).parent)]):
    if module_name == "dataset":
        continue

    importlib.import_module(f"{__name__}.{module_name}")

    __all__.append(module_name)