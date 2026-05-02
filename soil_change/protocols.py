"""Protocol interfaces used by the pipeline (Dependency Inversion).

These Protocols define *capabilities* instead of concrete classes.
The pipeline depends on these contracts, which means implementations can be
replaced without touching orchestration logic (DIP + Open/Closed Principle).
"""

from pathlib import Path
from typing import Protocol

import numpy as np


class BandReader(Protocol):
    def read_band(self, path: Path) -> tuple[np.ndarray, dict]:
        """Load one raster band and return `(array, metadata)`.

        Expected behavior:
        - `array` is a 2D numeric matrix (single band).
        - `metadata` carries geospatial profile (CRS, transform, dimensions, etc.)
          needed later to write GIS-aligned outputs.
        """


class RasterWriter(Protocol):
    def write(self, array: np.ndarray, meta: dict, path: Path) -> None:
        """Persist one array to disk using the provided geospatial metadata.

        Implementations must preserve spatial referencing so generated rasters can
        be opened correctly in GIS software.
        """


class ChangeClassifier(Protocol):
    def classify(self, diff: np.ndarray, threshold: float) -> np.ndarray:
        """Map continuous NDVI differences into semantic classes.

        Input:
        - `diff`: NDVI(date_2) - NDVI(date_1) array.
        - `threshold`: minimum absolute change to call a pixel "changed".

        Output convention in this project:
        - `-1`: vegetation loss
        - `0`: no significant change
        - `+1`: vegetation gain
        """


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
        """Render and save a human-readable summary figure.

        Intended use:
        - visual QA (quickly validate if maps look coherent),
        - portfolio/report communication artifact.
        """


class StatsReporter(Protocol):
    def print_change_stats(self, change: np.ndarray) -> None:
        """Print distribution metrics for the classified change map.

        Typical metrics include pixel counts and percentages by class.
        """
