"""Protocol interfaces used by the pipeline (Dependency Inversion)."""

from pathlib import Path
from typing import Protocol

import numpy as np


class BandReader(Protocol):
    def read_band(self, path: Path) -> tuple[np.ndarray, dict]:
        """Return raster data and metadata."""


class RasterWriter(Protocol):
    def write(self, array: np.ndarray, meta: dict, path: Path) -> None:
        """Persist one array to disk."""


class ChangeClassifier(Protocol):
    def classify(self, diff: np.ndarray, threshold: float) -> np.ndarray:
        """Classify NDVI difference map."""


class ResultsPlotter(Protocol):
    def plot(
        self,
        ndvi_1: np.ndarray,
        ndvi_2: np.ndarray,
        diff: np.ndarray,
        change: np.ndarray,
        label_1: str,
        label_2: str,
        threshold: float,
        output_path: Path,
    ) -> None:
        """Render and save figure."""


class StatsReporter(Protocol):
    def print_change_stats(self, change: np.ndarray) -> None:
        """Print distribution of change classes."""
