"""Lets the package call the sample-data generator without requiring `scripts` to be importable."""
from __future__ import annotations
import importlib.util
from pathlib import Path

_GEN = Path(__file__).resolve().parent.parent / "scripts" / "make_sample_data.py"


def generate(path: Path | str) -> None:
    spec = importlib.util.spec_from_file_location("make_sample_data", _GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main(str(path))
