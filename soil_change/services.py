"""Concrete implementations for reading, processing and reporting."""

from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import rasterio


class RasterioBandReader:
    """Single responsibility: read raster data from disk."""

    def read_band(self, path: Path) -> tuple[np.ndarray, dict]:
        with rasterio.open(path) as src:
            band = src.read(1).astype(np.float32)
            meta = src.meta.copy()
        return band, meta


class GeoTiffWriter:
    """Single responsibility: write arrays as GeoTIFF rasters."""

    def write(self, array: np.ndarray, meta: dict, path: Path) -> None:
        meta_out = meta.copy()
        meta_out.update(dtype="float32", count=1, driver="GTiff")
        with rasterio.open(path, "w", **meta_out) as dst:
            dst.write(array.astype(np.float32), 1)
        print(f"  ✓ Saved: {path}")


class NDVICalculator:
    """Single responsibility: NDVI computation."""

    @staticmethod
    def compute(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
        np.seterr(divide="ignore", invalid="ignore")
        denominator = nir + red
        ndvi = np.where(denominator == 0, np.nan, (nir - red) / denominator)
        return ndvi.astype(np.float32)


class ThresholdChangeClassifier:
    """Classify NDVI changes into loss/stable/gain classes."""

    def classify(self, diff: np.ndarray, threshold: float) -> np.ndarray:
        change = np.zeros_like(diff, dtype=np.float32)
        change[diff < -threshold] = -1
        change[diff > threshold] = 1
        return change


class ConsoleStatsReporter:
    """Single responsibility: print numeric summaries to stdout."""

    def print_change_stats(self, change: np.ndarray) -> None:
        valid_pixels = np.isfinite(change)
        total = int(np.sum(valid_pixels))
        if total == 0:
            print("\nNo valid pixels available for statistics.\n")
            return

        loss = int(np.sum(change == -1))
        gain = int(np.sum(change == 1))
        stable = int(np.sum(change == 0))

        print("\n── Change Statistics ──────────────────")
        print(f"  Vegetation loss : {loss:>8,} px  ({100 * loss / total:.1f}%)")
        print(f"  No change       : {stable:>8,} px  ({100 * stable / total:.1f}%)")
        print(f"  Vegetation gain : {gain:>8,} px  ({100 * gain / total:.1f}%)")
        print("────────────────────────────────────────\n")


class MatplotlibResultsPlotter:
    """Single responsibility: generate summary visualization."""

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
        fig, axes = plt.subplots(2, 2, figsize=(14, 11))
        fig.patch.set_facecolor("#0d1117")
        for ax in axes.flat:
            ax.set_facecolor("#0d1117")
            ax.tick_params(colors="#8b949e")
            for spine in ax.spines.values():
                spine.set_edgecolor("#30363d")

        def _imshow(
            ax: plt.Axes,
            data: np.ndarray,
            title: str,
            cmap: str,
            vmin: float,
            vmax: float,
            label: str = "NDVI",
        ) -> None:
            im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
            ax.set_title(title, color="white", fontsize=13, pad=10)
            cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label(label, color="#8b949e", fontsize=9)
            cbar.ax.yaxis.set_tick_params(color="#8b949e")
            plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#8b949e")
            ax.axis("off")

        _imshow(axes[0, 0], ndvi_1, f"NDVI — {label_1}", "RdYlGn", -0.2, 0.8)
        _imshow(axes[0, 1], ndvi_2, f"NDVI — {label_2}", "RdYlGn", -0.2, 0.8)
        _imshow(
            axes[1, 0],
            diff,
            f"NDVI Difference ({label_2} - {label_1})",
            "RdBu",
            -0.4,
            0.4,
            label="Delta NDVI",
        )

        cmap_change = mcolors.ListedColormap(["#f85149", "#8b949e", "#3fb950"])
        bounds = [-1.5, -0.5, 0.5, 1.5]
        norm = mcolors.BoundaryNorm(bounds, cmap_change.N)
        im = axes[1, 1].imshow(change, cmap=cmap_change, norm=norm)
        axes[1, 1].set_title(
            f"Change Map (threshold +/-{threshold})",
            color="white",
            fontsize=13,
            pad=10,
        )
        cbar = plt.colorbar(im, ax=axes[1, 1], fraction=0.046, pad=0.04, ticks=[-1, 0, 1])
        cbar.ax.set_yticklabels(["Loss", "No change", "Gain"], color="#8b949e")
        axes[1, 1].axis("off")

        fig.suptitle(
            "Sentinel-2 Vegetation Change Detection",
            color="white",
            fontsize=16,
            fontweight="bold",
            y=0.98,
        )
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"  ✓ Figure saved: {output_path}")
        plt.show()
