"""Configuration objects and default runtime setup."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScenePaths:
    """Container for one scene and its required bands."""

    label: str
    red: Path
    nir: Path


@dataclass(frozen=True)
class PipelineConfig:
    """High-level configuration for the change detection pipeline."""

    scene_1: ScenePaths
    scene_2: ScenePaths
    output_dir: Path
    change_threshold: float = 0.15


DATA_DIR = Path("data/10m")
OUTPUT_DIR = Path("outputs")
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

DEFAULT_CONFIG = PipelineConfig(
    scene_1=DATE_1,
    scene_2=DATE_2,
    output_dir=OUTPUT_DIR,
)
