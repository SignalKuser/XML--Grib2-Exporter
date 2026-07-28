from __future__ import annotations

from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from .model import Dataset, HeightSample, Station, VectorSample


TIME_FORMAT = "%d.%m.%Y %H:%M"


def _text(parent: ET.Element, name: str) -> str:
    value = parent.findtext(name)
    if value is None:
        raise ValueError(f"Pflichtelement <{name}> fehlt")
    return value.strip()


def parse_station(path: Path) -> Station:
    root = ET.parse(path).getroot()
    if root.tag not in {"Stream", "Port"}:
        raise ValueError(f"{path.name}: unbekanntes Wurzelelement <{root.tag}>")
    info = root.find("Info")
    if info is None:
        raise ValueError(f"{path.name}: <Info> fehlt")
    timezone = _text(info, "TimeZone")
    if timezone.upper() != "UTC":
        raise ValueError(f"{path.name}: Zeitzone ist {timezone!r}, erwartet wird UTC")
    common = dict(
        path=path,
        kind=root.tag.lower(),
        station_id=_text(info, "ID"),
        name=_text(info, "Name"),
        latitude=float(_text(info, "Lat")),
        longitude=float(_text(info, "Lon")),
        timezone=timezone,
        sample_minutes=int(_text(info, "SampleRate")),
        vectors=[],
        heights=[],
    )
    station = Station(**common)
    if root.tag == "Stream":
        for rate in root.findall("./Rates/Rate"):
            station.vectors.append(
                VectorSample(
                    datetime.strptime(_text(rate, "Time"), TIME_FORMAT),
                    float(_text(rate, "Speed")),
                    float(_text(rate, "Bearing")) % 360.0,
                )
            )
    else:
        for height in root.findall("./Heights/Height"):
            station.heights.append(
                HeightSample(
                    datetime.strptime(_text(height, "Time"), TIME_FORMAT),
                    float(_text(height, "Value")),
                )
            )
    if not station.vectors and not station.heights:
        raise ValueError(f"{path.name}: keine Zeitreihenwerte gefunden")
    return station


def load_dataset(source: str | Path) -> Dataset:
    source_path = Path(source)
    if source_path.is_file():
        paths = [source_path]
        root = source_path.parent
    else:
        paths = sorted(source_path.rglob("*.xml"))
        root = source_path
    if not paths:
        raise ValueError("Keine XML-Dateien gefunden")
    stations = [parse_station(path) for path in paths]
    streams = [station for station in stations if station.kind == "stream"]
    ports = [station for station in stations if station.kind == "port"]
    _validate_series(streams, "Strömung")
    _validate_series(ports, "Hafen")
    return Dataset(root=root, streams=streams, ports=ports)


def _validate_series(stations: list[Station], label: str) -> None:
    if not stations:
        return
    expected_interval = stations[0].sample_minutes
    expected_times = [
        sample.time
        for sample in (stations[0].vectors if stations[0].vectors else stations[0].heights)
    ]
    for station in stations:
        series = station.vectors if station.vectors else station.heights
        times = [sample.time for sample in series]
        if station.sample_minutes != expected_interval:
            raise ValueError(f"{label}: unterschiedliche Sample Period")
        if times != expected_times:
            raise ValueError(f"{label}: Zeitraster von {station.station_id} weicht ab")
