"""Unit tests for pipeline orchestration behavior using unittest."""

from dataclasses import dataclass, field
from pathlib import Path
import sys
import unittest

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from soil_change.config import PipelineConfig, ScenePaths
from soil_change.pipeline import ChangeDetectionPipeline


@dataclass
class FakeReader:
    """Test double that returns in-memory arrays in sequence."""

    arrays: list[np.ndarray]
    meta: dict
    calls: list[Path] = field(default_factory=list)
    _idx: int = 0

    def read_band(self, path: Path) -> tuple[np.ndarray, dict]:
        self.calls.append(path)
        array = self.arrays[self._idx]
        self._idx += 1
        return array, self.meta


@dataclass
class FakeWriter:
    """Test double that records write calls instead of touching disk."""

    writes: list[tuple[np.ndarray, dict, Path]] = field(default_factory=list)

    def write(self, array: np.ndarray, meta: dict, path: Path) -> None:
        self.writes.append((array.copy(), meta.copy(), path))


@dataclass
class FakeClassifier:
    """Test double classifier with deterministic output."""

    last_diff: np.ndarray | None = None
    last_threshold: float | None = None

    def classify(self, diff: np.ndarray, threshold: float) -> np.ndarray:
        self.last_diff = diff.copy()
        self.last_threshold = threshold
        return np.where(diff > threshold, 1.0, np.where(diff < -threshold, -1.0, 0.0)).astype(np.float32)


@dataclass
class FakePlotter:
    """Test double that only records plotting inputs."""

    called: bool = False
    payload: dict | None = None

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
        self.called = True
        self.payload = {
            "ndvi_1": ndvi_1.copy(),
            "ndvi_2": ndvi_2.copy(),
            "diff": diff.copy(),
            "change": change.copy(),
            "label_1": label_1,
            "label_2": label_2,
            "threshold": threshold,
            "output_path": output_path,
        }


@dataclass
class FakeStatsReporter:
    """Test double that records last change array."""

    called: bool = False
    last_change: np.ndarray | None = None

    def print_change_stats(self, change: np.ndarray) -> None:
        self.called = True
        self.last_change = change.copy()


class TestPipeline(unittest.TestCase):
    """Validate that the pipeline orchestrates all collaborators correctly."""

    def test_pipeline_run_orchestrates_all_steps(self) -> None:
        """Pipeline should read, compute, classify, write, report, and plot in order."""
        out_dir = Path("outputs")
        config = PipelineConfig(
            scene_1=ScenePaths(label="date_a", red=Path("a_red.jp2"), nir=Path("a_nir.jp2")),
            scene_2=ScenePaths(label="date_b", red=Path("b_red.jp2"), nir=Path("b_nir.jp2")),
            output_dir=out_dir,
            change_threshold=0.10,
        )

        red_1 = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        nir_1 = np.array([[2.0, 4.0], [6.0, 8.0]], dtype=np.float32)
        red_2 = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        nir_2 = np.array([[3.0, 3.0], [5.0, 7.0]], dtype=np.float32)
        meta = {"crs": "EPSG:32631", "transform": (1, 0, 0, 0, -1, 0), "width": 2, "height": 2}

        reader = FakeReader(arrays=[red_1, nir_1, red_2, nir_2], meta=meta)
        writer = FakeWriter()
        classifier = FakeClassifier()
        plotter = FakePlotter()
        stats_reporter = FakeStatsReporter()

        pipeline = ChangeDetectionPipeline(
            config=config,
            reader=reader,
            writer=writer,
            classifier=classifier,
            plotter=plotter,
            stats_reporter=stats_reporter,
        )

        pipeline.run()

        # 1) Reader usage (4 reads in expected order).
        self.assertEqual(
            reader.calls,
            [Path("a_red.jp2"), Path("a_nir.jp2"), Path("b_red.jp2"), Path("b_nir.jp2")],
        )

        # 2) Writer outputs (4 rasters with expected file names).
        written_paths = [path for _, _, path in writer.writes]
        self.assertEqual(
            written_paths,
            [
                out_dir / "ndvi_date_a.tif",
                out_dir / "ndvi_date_b.tif",
                out_dir / "ndvi_difference.tif",
                out_dir / "change_map.tif",
            ],
        )

        # 3) Ensure classifier receives NDVI difference and threshold.
        self.assertEqual(classifier.last_threshold, 0.10)
        self.assertIsNotNone(classifier.last_diff)

        # 4) Ensure downstream components are invoked with classified map.
        self.assertTrue(stats_reporter.called)
        self.assertIsNotNone(stats_reporter.last_change)
        self.assertTrue(plotter.called)
        self.assertIsNotNone(plotter.payload)
        self.assertEqual(plotter.payload["output_path"], out_dir / "change_detection_results.png")


if __name__ == "__main__":
    unittest.main()
