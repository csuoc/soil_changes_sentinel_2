"""Entrypoint script for Sentinel-2 NDVI change detection.

This file is intentionally tiny: its role is to expose one clear executable entry
point (`main`) and keep all domain logic inside `soil_change/`.
That separation helps future maintainers quickly understand where orchestration
starts and where implementation details live.
"""

from soil_change.pipeline import build_pipeline


def main() -> None:
    """Run the default pipeline configuration end to end.

    Detailed execution flow:
    1) Ask the factory (`build_pipeline`) to instantiate the pipeline object with
       all concrete dependencies already wired (reader, writer, classifier, etc.).
    2) Execute `.run()` to perform loading, NDVI computation, change
       classification, raster export, statistics, and final plotting.

    Keeping this function minimal provides two practical benefits:
    - easy CLI use (`python main.py`),
    - easy testability (the pipeline itself can be tested in isolation).
    """
    build_pipeline().run()


if __name__ == "__main__":
    main()
