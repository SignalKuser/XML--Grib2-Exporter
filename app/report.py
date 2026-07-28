from __future__ import annotations

import csv
from pathlib import Path

from .model import Dataset


def write_reports(dataset: Dataset, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "stations.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Typ", "ID", "Name", "Breite", "Länge", "Werte", "Zeitzone"])
        for station in dataset.ports + dataset.streams:
            writer.writerow(
                [
                    station.kind,
                    station.station_id,
                    station.name,
                    station.latitude,
                    station.longitude,
                    len(station.heights or station.vectors),
                    station.timezone,
                ]
            )
    lines = [
        "NLCurrent2GRIB v0.2.1 – Prüfbericht",
        f"Quelle: {dataset.root}",
        f"Zeitraum UTC: {dataset.start:%Y-%m-%d %H:%M} bis {dataset.end:%Y-%m-%d %H:%M}",
        f"Sample Period: {dataset.sample_minutes} Minuten",
        f"Häfen: {len(dataset.ports)}",
        f"Strömungspunkte: {len(dataset.streams)}",
        "Geschwindigkeit: Knoten (Eingabe), m/s (GRIB2)",
        "Bearing-Annahme: Fließrichtung (TO)",
        "GRIB2: discipline=10, category=1, U=2, V=3",
        "Hinweis: v0.2.1 erzeugt getrennte, maskierte Regionalraster.",
    ]
    (output_dir / "validation.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
