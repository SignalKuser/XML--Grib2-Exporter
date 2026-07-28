from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class VectorSample:
    time: datetime
    speed_knots: float
    bearing_to_degrees: float


@dataclass(frozen=True)
class HeightSample:
    time: datetime
    height_metres_alat: float


@dataclass
class Station:
    path: Path
    kind: str
    station_id: str
    name: str
    latitude: float
    longitude: float
    timezone: str
    sample_minutes: int
    vectors: list[VectorSample]
    heights: list[HeightSample]


@dataclass
class Dataset:
    root: Path
    streams: list[Station]
    ports: list[Station]

    @property
    def start(self) -> datetime:
        series = self.streams[0].vectors if self.streams else self.ports[0].heights
        return series[0].time

    @property
    def end(self) -> datetime:
        series = self.streams[0].vectors if self.streams else self.ports[0].heights
        return series[-1].time

    @property
    def sample_minutes(self) -> int:
        stations = self.streams or self.ports
        return stations[0].sample_minutes
