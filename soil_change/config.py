"""Configuration objects and default runtime setup.

This module centralizes every "what should be processed?" decision:
- which two scenes are compared,
- where outputs are written,
- which threshold defines relevant change.

In a production workflow, this could be fed by CLI args or external config files.
For this portfolio project, static defaults keep the execution reproducible.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScenePaths:
    """Container for one scene and its required bands.

    Attributes:
    - label: human-readable identifier used in output filenames/plots.
    - red: path to Sentinel-2 B04 (red) band file.
    - nir: path to Sentinel-2 B08 (near-infrared) band file.

    Why these two bands:
    NDVI relies specifically on RED and NIR reflectance to approximate
    vegetation vigor/activity.

    Sentinel-2 reference:
    - B04 corresponds to the red spectral region.
    - B08 corresponds to the near-infrared (NIR) spectral region.
    Both are commonly used together for NDVI and are available at 10 m in
    Sentinel-2 L2A products.
    """

    label: str
    red: Path
    nir: Path


@dataclass(frozen=True)
class PipelineConfig:
    """High-level configuration for the change detection pipeline.

    Attributes:
    - scene_1 / scene_2: the two acquisition dates to compare.
    - output_dir: folder where GeoTIFF and PNG artifacts are persisted.
    - change_threshold: absolute NDVI-difference cutoff used to classify pixels:
        diff < -threshold  -> vegetation loss (-1)
        |diff| <= threshold -> stable/no relevant change (0)
        diff > threshold   -> vegetation gain (+1)
    """

    scene_1: ScenePaths
    scene_2: ScenePaths
    output_dir: Path
    change_threshold: float = 0.15


DATA_DIR = Path("data/10m")
OUTPUT_DIR = Path("outputs")
# Ensure the output folder exists before the pipeline tries writing files.
OUTPUT_DIR.mkdir(exist_ok=True)

DATE_1 = ScenePaths(
    label="2025-11",
    red=DATA_DIR / "2025-11-22/T31TCF_20251122T104249_B04_10m.jp2",
    nir=DATA_DIR / "2025-11-22/T31TCF_20251122T104249_B08_10m.jp2",
)

DATE_2 = ScenePaths(
    label="2023-12",
    red=DATA_DIR / "2026-04-26/T31TCF_20260426T104021_B04_10m.jp2",
    nir=DATA_DIR / "2026-04-26/T31TCF_20260426T104021_B08_10m.jp2",
)

# Default configuration used by `build_pipeline()`.
# Editing this object is the quickest way to run new comparisons.
DEFAULT_CONFIG = PipelineConfig(
    scene_1=DATE_1,
    scene_2=DATE_2,
    output_dir=OUTPUT_DIR,
)
