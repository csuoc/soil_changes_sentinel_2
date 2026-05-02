# Sentinel-2 Vegetation Change Detection

NDVI-based vegetation change detection between two Sentinel-2 dates, using real `.jp2` bands and producing GIS-ready outputs.

## Overview

This project compares two Sentinel-2 scenes of the same area and computes:

- NDVI for date 1
- NDVI for date 2
- NDVI difference (`date_2 - date_1`)
- Classified change map (`-1`, `0`, `+1`)
- A 4-panel summary figure for quick visual validation

NDVI formula:

```text
NDVI = (NIR - Red) / (NIR + Red)
```

- `B04` = Red
- `B08` = NIR

## Current architecture (SOLID-oriented)

The pipeline was split into focused modules to keep responsibilities clear:

```text
soil_changes_sentinel_2/
├── analysis.py                # Entrypoint script
├── soil_change/
│   ├── __init__.py
│   ├── config.py              # Scene paths + pipeline config dataclasses
│   ├── protocols.py           # Interfaces (Protocol) for DIP
│   ├── services.py            # Concrete implementations (reader/writer/etc.)
│   └── pipeline.py            # Orchestration + dependency wiring
├── data/
│   └── 10m/
├── outputs/
├── requirements.txt
└── README.md
```

### Why this split?

- Easier to maintain and test each part independently
- Clear extension points (replace classifier/plotter/writer without changing orchestration)
- Better compliance with SOLID principles for future growth

## Installation

```bash
pip install -r requirements.txt
```

## Configure your scenes

Update scene paths in `soil_change/config.py`:

- `DATE_1`: label + `B04` + `B08`
- `DATE_2`: label + `B04` + `B08`
- `change_threshold` (optional) in `DEFAULT_CONFIG`

Expected input location pattern:

```text
data/10m/<date_folder>/<band_file>.jp2
```

## Run

```bash
python analysis.py
```

This will generate outputs in `outputs/`.

## Outputs

- `ndvi_<label>.tif`: NDVI raster per date (GeoTIFF)
- `ndvi_difference.tif`: continuous NDVI difference map
- `change_map.tif`: thresholded classes (`-1` loss, `0` stable, `+1` gain)
- `change_detection_results.png`: 4-panel visual summary

## Data source

Download Sentinel-2 L2A products from [Copernicus Data Space](https://dataspace.copernicus.eu/).

Recommended:

- same tile and area for both dates
- low cloud coverage scenes
- similar seasonal context when possible

## Next improvements

- Cloud masking with SCL band before NDVI calculation
- Add additional indices (NDWI, NBR, NDBI)
- Batch multi-date runs
- Unit tests with synthetic rasters
- Optional CLI arguments for paths and threshold

## License

MIT
