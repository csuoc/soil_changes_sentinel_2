"""Sentinel-2 vegetation change detection package."""

from .pipeline import ChangeDetectionPipeline, build_pipeline

__all__ = ["ChangeDetectionPipeline", "build_pipeline"]
