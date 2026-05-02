"""Pipeline orchestration and dependency wiring."""

from .config import DEFAULT_CONFIG, PipelineConfig
from .protocols import BandReader, ChangeClassifier, RasterWriter, ResultsPlotter, StatsReporter
from .services import (
    ConsoleStatsReporter,
    GeoTiffWriter,
    MatplotlibResultsPlotter,
    NDVICalculator,
    RasterioBandReader,
    ThresholdChangeClassifier,
)


class ChangeDetectionPipeline:
    """Orchestrates workflow using abstractions (Open/Closed + DIP)."""

    def __init__(
        self,
        config: PipelineConfig,
        reader: BandReader,
        writer: RasterWriter,
        classifier: ChangeClassifier,
        plotter: ResultsPlotter,
        stats_reporter: StatsReporter,
    ) -> None:
        self.config = config
        self.reader = reader
        self.writer = writer
        self.classifier = classifier
        self.plotter = plotter
        self.stats_reporter = stats_reporter

    def run(self) -> None:
        print("\nSentinel-2 Change Detection Pipeline\n")
        scene_1 = self.config.scene_1
        scene_2 = self.config.scene_2
        out_dir = self.config.output_dir

        print("-> Loading bands...")
        red_1, meta = self.reader.read_band(scene_1.red)
        nir_1, _ = self.reader.read_band(scene_1.nir)
        red_2, _ = self.reader.read_band(scene_2.red)
        nir_2, _ = self.reader.read_band(scene_2.nir)

        print("-> Computing NDVI...")
        ndvi_1 = NDVICalculator.compute(red_1, nir_1)
        ndvi_2 = NDVICalculator.compute(red_2, nir_2)

        print("-> Computing NDVI difference...")
        diff = ndvi_2 - ndvi_1

        print("-> Classifying changes...")
        change = self.classifier.classify(diff, self.config.change_threshold)

        print("-> Saving outputs...")
        self.writer.write(ndvi_1, meta, out_dir / f"ndvi_{scene_1.label}.tif")
        self.writer.write(ndvi_2, meta, out_dir / f"ndvi_{scene_2.label}.tif")
        self.writer.write(diff, meta, out_dir / "ndvi_difference.tif")
        self.writer.write(change, meta, out_dir / "change_map.tif")

        self.stats_reporter.print_change_stats(change)

        print("-> Generating figure...")
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
    """Factory to wire default concrete dependencies."""
    return ChangeDetectionPipeline(
        config=DEFAULT_CONFIG,
        reader=RasterioBandReader(),
        writer=GeoTiffWriter(),
        classifier=ThresholdChangeClassifier(),
        plotter=MatplotlibResultsPlotter(),
        stats_reporter=ConsoleStatsReporter(),
    )
