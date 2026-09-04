#!/usr/bin/env python3
"""Read-only benchmark using only REVIEW.md's five painted copies and six result URLs.

Run from any directory. Refuses to overwrite an earlier run; move its output first
or pass --out to choose a fresh directory. Requires gdoc, uv, Chrome and Poppler.
"""

import argparse
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCOUNT = "alejandro.acelas-contractor@80000hours.org"


def run(cmd):
    start = time.monotonic()
    result = subprocess.run(cmd, capture_output=True, text=True)
    record = {
        "command": list(map(str, cmd)),
        "seconds": round(time.monotonic() - start, 4),
        "exit": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, default=ROOT / "micro/shots-benchmark/20260904"
    )
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    records = []

    def record(cmd, **labels):
        result = {**labels, **run(cmd)}
        records.append(result)
        (args.out / "runs.json").write_text(json.dumps(records, indent=2) + "\n")
        print(
            json.dumps({k: result[k] for k in ["kind", "case", "seconds", "exit"]}),
            flush=True,
        )
        return result

    def info(url, name, phase):
        return record(
            ["gdoc", "info", "--account", ACCOUNT, "--quiet", "--json", url],
            kind="metadata-" + phase,
            case=name,
        )

    review = (ROOT / "REVIEW.md").read_text().split("## collab/v01")[0]
    copies = re.findall(r"\*\*([^*]+?)/v01\*\* — (https://docs.google.com/\S+)", review)
    assert len(copies) == 5
    for name, url in copies:
        info(url, name, "before")
        for phase in ["first", "warm"]:
            record(
                [
                    str(ROOT / "bin/gdt-shot-headless"),
                    url,
                    str(args.out / "painted" / name / phase),
                    *(["--cold-cache"] if phase == "first" else []),
                ],
                kind="browser-" + phase,
                case=name,
            )
        info(url, name, "after")

    for path in sorted((ROOT / "micro/results/20260904").glob("*/result.json")):
        result = json.loads(path.read_text())
        name, url = result["name"], result["doc"]
        out = args.out / "micro" / name
        out.mkdir(parents=True)
        info(url, name, "before")
        record(
            [str(ROOT / "bin/gdt-shot-headless"), url, str(out / "browser")],
            kind="micro-browser",
            case=name,
        )
        exported = record(
            [
                "gdoc",
                "export",
                "--account",
                ACCOUNT,
                "--quiet",
                "--format",
                "pdf",
                "--out",
                str(out / "export.pdf"),
                url,
            ],
            kind="pdf-export",
            case=name,
        )
        if exported["exit"] == 0:
            record(
                [
                    "pdftoppm",
                    "-r",
                    "150",
                    "-png",
                    str(out / "export.pdf"),
                    str(out / "pdf"),
                ],
                kind="pdf-render",
                case=name,
            )
            record(["pdfinfo", str(out / "export.pdf")], kind="pdf-info", case=name)
            record(["pdffonts", str(out / "export.pdf")], kind="pdf-fonts", case=name)
        info(url, name, "after")
    if any(r["exit"] for r in records):
        raise SystemExit("Some benchmark commands failed; see runs.json")


if __name__ == "__main__":
    main()
