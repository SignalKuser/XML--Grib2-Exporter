from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import re

import numpy as np
from eccodes import (
    codes_grib_new_from_samples,
    codes_release,
    codes_set,
    codes_set_values,
    codes_write,
)

from .model import Dataset, Station


KNOT_TO_METRES_PER_SECOND = 0.5144444444444445
MISSING_VALUE = 9999.0


@dataclass
class RegionalGrid:
    code: str
    stations: list[Station]
    lon_min: float
    lon_max: float
    lat_min: float
    lat_max: float
    ni: int
    nj: int
    di: float
    dj: float
    neighbour_indexes: np.ndarray
    neighbour_weights: np.ndarray
    valid: np.ndarray


def region_code(station_id: str) -> str:
    match = re.match(r"([A-Za-z_]+)", station_id)
    return match.group(1).upper() if match else "NL"


def group_streams(dataset: Dataset) -> dict[str, list[Station]]:
    groups: dict[str, list[Station]] = {}
    for station in dataset.streams:
        groups.setdefault(region_code(station.station_id), []).append(station)
    return dict(sorted(groups.items()))


def _nearest_spacing_degrees(stations: list[Station]) -> float:
    if len(stations) < 2:
        return 0.05
    mean_lat = sum(s.latitude for s in stations) / len(stations)
    scale_x = math.cos(math.radians(mean_lat))
    xy = np.asarray(
        [(s.longitude * scale_x, s.latitude) for s in stations], dtype=np.float64
    )
    nearest = []
    for index in range(len(xy)):
        distances = np.sqrt(np.sum((xy - xy[index]) ** 2, axis=1))
        distances[index] = np.inf
        nearest.append(float(np.min(distances)))
    spacing = float(np.median(nearest))
    return min(0.10, max(0.005, spacing))


def build_regional_grid(code: str, stations: list[Station]) -> RegionalGrid:
    if len(stations) < 3:
        raise ValueError(f"Region {code}: mindestens drei Strömungspunkte erforderlich")
    mean_lat = sum(s.latitude for s in stations) / len(stations)
    scale_x = math.cos(math.radians(mean_lat))
    spacing = _nearest_spacing_degrees(stations)
    lons = np.asarray([s.longitude for s in stations], dtype=np.float64)
    lats = np.asarray([s.latitude for s in stations], dtype=np.float64)
    lon_min, lon_max = float(np.min(lons)), float(np.max(lons))
    lat_min, lat_max = float(np.min(lats)), float(np.max(lats))
    ni = max(2, int(math.ceil((lon_max - lon_min) / spacing)) + 1)
    nj = max(2, int(math.ceil((lat_max - lat_min) / spacing)) + 1)
    di = (lon_max - lon_min) / (ni - 1)
    dj = (lat_max - lat_min) / (nj - 1)

    source_xy = np.column_stack((lons * scale_x, lats))
    target_xy = []
    for j in range(nj):
        lat = lat_max - j * dj
        for i in range(ni):
            lon = lon_min + i * di
            target_xy.append((lon * scale_x, lat))
    target_xy = np.asarray(target_xy, dtype=np.float64)
    distances = np.sqrt(
        np.sum((target_xy[:, None, :] - source_xy[None, :, :]) ** 2, axis=2)
    )
    neighbour_count = min(4, len(stations))
    indexes = np.argsort(distances, axis=1)[:, :neighbour_count]
    selected = np.take_along_axis(distances, indexes, axis=1)
    valid = selected[:, 0] <= spacing * 1.35
    exact = selected[:, 0] < 1e-10
    weights = np.zeros_like(selected)
    weights[~exact] = 1.0 / np.maximum(selected[~exact], 1e-12) ** 2
    weights[~exact] /= np.sum(weights[~exact], axis=1, keepdims=True)
    weights[exact, 0] = 1.0

    return RegionalGrid(
        code=code,
        stations=stations,
        lon_min=lon_min,
        lon_max=lon_max,
        lat_min=lat_min,
        lat_max=lat_max,
        ni=ni,
        nj=nj,
        di=di,
        dj=dj,
        neighbour_indexes=indexes,
        neighbour_weights=weights,
        valid=valid,
    )


def _source_components(stations: list[Station], index: int, component: str):
    values = []
    for station in stations:
        sample = station.vectors[index]
        radians = math.radians(sample.bearing_to_degrees)
        speed = sample.speed_knots * KNOT_TO_METRES_PER_SECOND
        values.append(speed * (math.sin(radians) if component == "u" else math.cos(radians)))
    return np.asarray(values, dtype=np.float64)


def _grid_values(grid: RegionalGrid, source_values: np.ndarray):
    selected = source_values[grid.neighbour_indexes]
    values = np.sum(selected * grid.neighbour_weights, axis=1)
    values[~grid.valid] = MISSING_VALUE
    return values


def _write_message(handle, output, grid, valid_time, base_time, number, values):
    settings = {
        "discipline": 10,
        "parameterCategory": 1,
        "parameterNumber": number,
        "productDefinitionTemplateNumber": 0,
        "typeOfFirstFixedSurface": 1,
        "scaledValueOfFirstFixedSurface": 0,
        "Ni": grid.ni,
        "Nj": grid.nj,
        "latitudeOfFirstGridPointInDegrees": grid.lat_max,
        "longitudeOfFirstGridPointInDegrees": grid.lon_min,
        "latitudeOfLastGridPointInDegrees": grid.lat_min,
        "longitudeOfLastGridPointInDegrees": grid.lon_max,
        "iDirectionIncrementInDegrees": grid.di,
        "jDirectionIncrementInDegrees": grid.dj,
        "iScansNegatively": 0,
        "jScansPositively": 0,
        "dataDate": int(base_time.strftime("%Y%m%d")),
        "dataTime": int(base_time.strftime("%H%M")),
        "indicatorOfUnitOfTimeRange": 0,
        "forecastTime": int((valid_time - base_time).total_seconds() // 60),
        "bitmapPresent": 1,
        "missingValue": MISSING_VALUE,
        "bitsPerValue": 16,
    }
    for key, value in settings.items():
        codes_set(handle, key, value)
    codes_set_values(handle, values)
    codes_write(handle, output)


def write_region_grib(grid: RegionalGrid, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    base_time = grid.stations[0].vectors[0].time
    with output_path.open("wb") as output:
        for index, sample in enumerate(grid.stations[0].vectors):
            for component, parameter_number in (("u", 2), ("v", 3)):
                handle = codes_grib_new_from_samples("regular_ll_sfc_grib2")
                try:
                    source = _source_components(grid.stations, index, component)
                    values = _grid_values(grid, source)
                    _write_message(
                        handle,
                        output,
                        grid,
                        sample.time,
                        base_time,
                        parameter_number,
                        values,
                    )
                finally:
                    codes_release(handle)
    return output_path


def write_current_gribs(dataset: Dataset, output_dir: str | Path) -> list[Path]:
    output_dir = Path(output_dir)
    results = []
    for code, stations in group_streams(dataset).items():
        grid = build_regional_grid(code, stations)
        filename = (
            f"NL_Current_{code}_{dataset.start:%Y%m%d}_"
            f"{dataset.sample_minutes}min.grb2"
        )
        results.append(write_region_grib(grid, output_dir / filename))
    return results
