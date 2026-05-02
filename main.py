"""Entrypoint script for Sentinel-2 NDVI change detection."""

from soil_change.pipeline import build_pipeline


def main() -> None:
    """Run the default pipeline."""
    build_pipeline().run()


if __name__ == "__main__":
    main()
