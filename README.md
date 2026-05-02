# Sentinel-2 Vegetation Change Detection

Remote sensing project for detecting vegetation change between two dates using Sentinel-2 L2A bands (`B04` and `B08`), computing NDVI, classifying change, and producing geospatial outputs ready for GIS analysis.

## Analysis Objective

The main goal is to build a reproducible and explainable workflow that can:

- measure temporal variation in vegetation cover/activity,
- identify areas with vegetation loss, stability, or gain,
- deliver quantitative and visual outputs in a reusable format.

This repository is intended as a technical portfolio piece: it not only runs the analysis, but also demonstrates a clean architecture (influenced by SOLID principles) to support maintainability and extension.

## Methodological Basis (NDVI)

NDVI is computed as:

```text
NDVI = (NIR - Red) / (NIR + Red)
```

Where:

- `B04` = Red band
- `B08` = Near-infrared band (NIR)

General interpretation:

- high NDVI values are typically associated with denser / healthier vegetation,
- low or negative values are typically associated with bare soil, water, urban surfaces, or strongly degraded vegetation.

## Workflow Followed (Step by Step)

1. **Raster data loading**  
   Two scenes covering the same area are read (two different dates), extracting bands `B04` and `B08` for each date.

2. **NDVI calculation per date**  
   An NDVI map is computed for each date with numerical handling for invalid divisions.

3. **Temporal difference**  
   `diff = NDVI_date_2 - NDVI_date_1` is computed to capture continuous pixel-by-pixel change.

4. **Threshold-based classification**  
   The continuous difference is converted into discrete classes:
   - `-1`: vegetation loss (`diff < -threshold`)
   - `0`: no significant change (`|diff| <= threshold`)
   - `+1`: vegetation gain (`diff > threshold`)

5. **Output export**  
   GeoTIFF files are written for NDVI date 1, NDVI date 2, NDVI difference, and the classified change map.

6. **Descriptive statistics**  
   Pixel counts and percentages are reported by class to interpret change magnitude.

7. **Final visualization**  
   A 4-panel figure is generated for fast review and result communication.

## Project Architecture

```text
soil_changes_sentinel_2/
├── main.py                    # Minimal entrypoint: builds and runs the pipeline
├── soil_change/
│   ├── __init__.py
│   ├── config.py              # Configuration dataclasses and default paths
│   ├── protocols.py           # Contracts (Protocol) for DIP
│   ├── services.py            # Concrete implementations (IO, NDVI, classification, plots)
│   └── pipeline.py            # Workflow orchestration + dependency injection
├── data/
│   └── 10m/                   # Input Sentinel-2 bands
├── outputs/                   # Generated results (GeoTIFF + PNG)
├── requirements.txt
└── README.md
```

### Why this architecture?

- It separates technical responsibilities by module.
- It allows components to be replaced without rewriting orchestration.
- It improves readability for technical review (interview / portfolio context).

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `soil_change/config.py`:

- `DATE_1`: label and `B04` / `B08` paths for the baseline date.
- `DATE_2`: label and `B04` / `B08` paths for the comparison date.
- `change_threshold` in `DEFAULT_CONFIG` to tune sensitivity.

Expected input pattern:

```text
data/10m/<date_folder>/<band_file>.jp2
```

## Run

```bash
python main.py
```

Results will be generated in `outputs/`.

## Generated Outputs

- `ndvi_<label>.tif`: NDVI per date (georeferenced GeoTIFF).
- `ndvi_difference.tif`: continuous NDVI change (`date_2 - date_1`).
- `change_map.tif`: classified map (`-1`, `0`, `+1`).
- `change_detection_results.png`: 4-panel visual dashboard.

## Primary Conclusions (Current Run)

![Detection Result](./outputs/change_detection_results.png)

With the configuration and data currently included in the repository, the resulting statistics are:

- **Vegetation loss:** 36,199,811 px (**30.0%**)
- **No significant change:** 84,197,376 px (**69.8%**)
- **Vegetation gain:** 163,213 px (**0.1%**)

Initial interpretation:

- Spatial stability dominates the scene (almost 70%).
- There is a relevant proportion of vegetation loss (~30%) that deserves geographic inspection.
- Detected gain is marginal compared with the loss signal.

> Technical note: these conclusions are sensitive to cloud contamination, seasonality, acquisition geometry, and the chosen threshold. For operational decision-making, cloud/SCL masking and additional validation are recommended.

## Data Source

Sentinel-2 L2A products are available from [Copernicus Data Space](https://dataspace.copernicus.eu/).

Recommended good practices for robust comparisons:

- same tile and geographic extent,
- low cloud coverage in both dates,
- comparable phenological / seasonal context whenever possible.

## Suggested Future Improvements

- Cloud / shadow masking using the SCL band.
- Multi-index analysis (NDWI, NBR, NDBI) for stronger robustness.
- Batch execution for longer time series.
- Unit tests with synthetic rasters.
- CLI parameterization (paths, threshold, output).

## License

MIT
