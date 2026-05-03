"""Pipeline orchestration and dependency wiring.

This module contains:
1) the workflow coordinator (`ChangeDetectionPipeline`),
2) a factory function (`build_pipeline`) that injects default implementations.

The coordinator focuses on sequencing and business flow, not low-level details.

Collaborators injected into `ChangeDetectionPipeline` must provide the methods
that `run()` calls on them (`read_band`, `write`, `classify`, `plot`,
`print_change_stats`). Typical implementations live in `services.py`; tests
often pass small substitutes with the same method names — no inheritance needed.
"""

from typing import Any

from .config import DEFAULT_CONFIG, PipelineConfig
from .services import (
    ConsoleStatsReporter,
    GeoTiffWriter,
    MatplotlibResultsPlotter,
    NDVICalculator,
    RasterioBandReader,
    ThresholdChangeClassifier,
)


class ChangeDetectionPipeline:
    """Runs the NDVI workflow; collaborators are injected in `__init__`."""

    def __init__(
        self,
        config: PipelineConfig,
        reader: Any,
        writer: Any,
        classifier: Any,
        plotter: Any,
        stats_reporter: Any,
    ) -> None:
        # Save all dependencies as instance attributes so they are available through
        # the pipeline lifecycle and can be mocked/replaced in tests.
        self.config = config
        self.reader = reader
        self.writer = writer
        self.classifier = classifier
        self.plotter = plotter
        self.stats_reporter = stats_reporter

    def run(self) -> None:
        """Execute the full two-date NDVI change-detection workflow.

        High-level stages:
        1) Load required RED/NIR bands for both dates.
        2) Compute NDVI per date.
        3) Compute temporal delta (`date_2 - date_1`).
        4) Classify delta into loss/stable/gain categories.
        5) Persist all raster outputs.
        6) Print descriptive statistics.
        7) Build a 4-panel summary figure.
        """
        print("\nSentinel-2 Change Detection Pipeline\n")
        scene_1 = self.config.scene_1
        scene_2 = self.config.scene_2
        out_dir = self.config.output_dir

        print("-> Loading bands...")
        # Read first date (baseline/reference date).
        red_1, meta = self.reader.read_band(scene_1.red)
        nir_1, _ = self.reader.read_band(scene_1.nir)
        # Read second date (comparison/current date).
        red_2, _ = self.reader.read_band(scene_2.red)
        nir_2, _ = self.reader.read_band(scene_2.nir)

        print("-> Computing NDVI...")
        # NDVI is computed independently for each date.
        ndvi_1 = NDVICalculator.compute(red_1, nir_1)
        ndvi_2 = NDVICalculator.compute(red_2, nir_2)

        print("-> Computing NDVI difference...")
        # Positive values indicate NDVI increase; negative values indicate decrease.
        diff = ndvi_2 - ndvi_1

        print("-> Classifying changes...")
        # Convert continuous delta map into discrete classes for easier interpretation.
        change = self.classifier.classify(diff, self.config.change_threshold)

        print("-> Saving outputs...")
        # Reuse metadata from the source rasters so outputs keep geospatial alignment.
        self.writer.write(ndvi_1, meta, out_dir / f"ndvi_{scene_1.label}.tif")
        self.writer.write(ndvi_2, meta, out_dir / f"ndvi_{scene_2.label}.tif")
        self.writer.write(diff, meta, out_dir / "ndvi_difference.tif")
        self.writer.write(change, meta, out_dir / "change_map.tif")

        # Provide quick quantitative insight directly in the terminal.
        self.stats_reporter.print_change_stats(change)

        print("-> Generating figure...")
        # Generate publication-friendly visual summary that combines all key products.
        self.plotter.plot(
            ndvi_1=ndvi_1,
            ndvi_2=ndvi_2,
            diff=diff,
            change=change,
            label_1=scene_1.label,
            label_2=scene_2.label,
            threshold=self.config.change_threshold,
            output_path=out_dir / "change_detection_results.png",
        )
        print("Pipeline complete!\n")


def build_pipeline() -> ChangeDetectionPipeline:
    """Factory to wire default concrete dependencies.

    Centralizing wiring in one place avoids scattering object-construction logic
    across files and keeps the entrypoint clean.
    """
    return ChangeDetectionPipeline(
        config=DEFAULT_CONFIG,
        reader=RasterioBandReader(),
        writer=GeoTiffWriter(),
        classifier=ThresholdChangeClassifier(),
        plotter=MatplotlibResultsPlotter(),
        stats_reporter=ConsoleStatsReporter(),
    )
