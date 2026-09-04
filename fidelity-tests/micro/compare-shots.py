#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pillow==12.1.1"]
# ///
"""Make aligned browser/PDF crops from benchmark output; no document access.

Usage: ./compare-shots.py shots-benchmark/20260904-final
Stitch viewport page bands using recorded canvas geometry. Locate crop regions in
PDF text only, never the Google Docs DOM. Original captures remain untouched.
"""

import argparse
import json
import math
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    for case in sorted((args.run / "micro").iterdir()):
        meta = json.loads((case / "browser/capture.json").read_text())
        box = meta["views"][0]["pages"][0]
        size = (round(box["width"]), round(box["height"]))
        stitched = Image.new("RGB", size, "white")
        coverage = set()
        for view in meta["views"]:
            assert len(view["pages"]) == 1, "Micro comparison expects one-page fixtures"
            rect = view["pages"][0]
            screenshot = Image.open(case / "browser" / view["image"])
            # The editor starts immediately below the toolbar/ruler.
            editor_top = screenshot.height - view["clientHeight"]
            top = max(editor_top, math.ceil(rect["y"]))
            bottom = min(screenshot.height, round(rect["y"] + rect["height"]))
            y = round(top - rect["y"])
            band = screenshot.crop(
                (round(rect["x"]), top, round(rect["x"]) + size[0], bottom)
            )
            stitched.paste(band, (0, y))
            coverage.update(range(y, y + band.height))
        assert set(range(size[1])).issubset(coverage), f"{case.name}: missing page rows"
        stitched.save(case / "browser-page.png")
        pdf = (
            Image.open(case / "pdf-1.png")
            .convert("RGB")
            .resize(size, Image.Resampling.LANCZOS)
        )
        xml = subprocess.check_output(
            ["pdftotext", "-bbox", str(case / "export.pdf"), "-"]
        )
        root = ET.fromstring(xml)
        page = root.find(".//{*}page")
        words = list(page.iterfind(".//{*}word"))
        factor = size[0] / float(page.attrib["width"])
        groups = {
            "body": [w for w in words if float(w.attrib["yMin"]) < 500],
            "footnote": [w for w in words if float(w.attrib["yMin"]) >= 500],
        }
        crops = {}
        for group, items in groups.items():
            if not items:
                continue
            bounds = (
                max(
                    0,
                    math.floor(min(float(w.attrib["xMin"]) for w in items) * factor)
                    - 20,
                ),
                max(
                    0,
                    math.floor(min(float(w.attrib["yMin"]) for w in items) * factor)
                    - 20,
                ),
                min(
                    size[0],
                    math.ceil(max(float(w.attrib["xMax"]) for w in items) * factor)
                    + 20,
                ),
                min(
                    size[1],
                    math.ceil(max(float(w.attrib["yMax"]) for w in items) * factor)
                    + 20,
                ),
            )
            for label, image in [("browser", stitched), ("pdf", pdf)]:
                image.crop(bounds).save(case / f"{label}-{group}.png")
            crops[group] = bounds
        (case / "comparison.json").write_text(
            json.dumps(
                {
                    "page_size_css_px": size,
                    "crop_bounds": crops,
                    "pdf_scale": factor,
                    "browser_rows_covered": len(coverage),
                },
                indent=2,
            )
            + "\n"
        )
        print(case.name)


if __name__ == "__main__":
    main()
