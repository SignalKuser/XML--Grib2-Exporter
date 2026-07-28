from __future__ import annotations

import argparse
from pathlib import Path

from app.grib_output import write_current_gribs
from app.report import write_reports
from app.xml_input import load_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="NL XML currents to GRIB2 prototype")
    parser.add_argument("input", help="UTC XML export folder")
    parser.add_argument("output", help="Output folder")
    args = parser.parse_args()
    dataset = load_dataset(args.input)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    gribs = write_current_gribs(dataset, output)
    write_reports(dataset, output)
    for grib in gribs:
        print(grib)


if __name__ == "__main__":
    main()
