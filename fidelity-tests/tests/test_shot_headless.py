"""Local browser tests; never visit a Google Doc or use login credentials.

Run with uv, playwright==1.62.0, and pytest; see micro/README.md.
"""

import importlib.machinery
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

SCRIPT = Path(__file__).resolve().parents[1] / "bin/gdt-shot-headless"
loader = importlib.machinery.SourceFileLoader("shooter", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
shooter = importlib.util.module_from_spec(spec)
loader.exec_module(shooter)


@pytest.fixture
def page():
    if not Path(shooter.CHROME).exists():
        pytest.skip("Requires installed Google Chrome on macOS")
    shooter.PROFILE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="local-test-", dir=shooter.PROFILE
    ) as profile:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                profile,
                executable_path=shooter.CHROME,
                headless=True,
                viewport=shooter.VIEWPORT,
            )
            page = context.pages[0]
            page.set_content("""<style>body{margin:0}.kix-appview-editor {
                height:699px;overflow:auto}.content{height:1450px;
                background:linear-gradient(red,blue)}</style>
                <div class="kix-appview-editor"><div class="content"></div></div>""")
            yield page
            context.close()


def test_offsets_cover_bottom_and_file_legacy_manifest(page, tmp_path):
    records = shooter.capture(page, tmp_path, None)
    assert [r["requested"] for r in records] == [0, 650, 1300]
    assert [r["actual"] for r in records] == [0, 650, 751]
    out = tmp_path / "filed"
    subprocess.run(
        [
            str(SCRIPT.with_name("gdt-shot")),
            str(out),
            "--step",
            "650",
            *map(str, sorted(tmp_path.glob("raw-*.jpg"))),
        ],
        check=True,
    )
    manifest = json.loads((out / "shot.json").read_text())
    assert manifest["views"] == 3
    assert manifest["scroll_step_px"] == 650
    assert sorted(p.name for p in out.glob("view-*")) == [
        "view-01.jpg",
        "view-02.jpg",
        "view-03.jpg",
    ]
    assert page.viewport_size == {"width": 1440, "height": 828}


def test_explicit_count_keeps_clamped_offsets(page, tmp_path):
    records = shooter.capture(page, tmp_path, 4)
    assert [r["requested"] for r in records] == [0, 650, 1300, 1950]
    assert [r["actual"] for r in records] == [0, 650, 751, 751]


def test_refuses_foreign_browser(monkeypatch):
    monkeypatch.setattr(shooter, "endpoint_ready", lambda: True)
    monkeypatch.setattr(shooter, "dedicated_browser", lambda: False)
    with pytest.raises(RuntimeError, match="refusing to attach"):
        shooter.connect_chrome()


def test_existing_capture_is_not_overwritten(monkeypatch, tmp_path):
    marker = tmp_path / "shot.json"
    marker.write_text('{"views": 9}')
    monkeypatch.setattr(
        "sys.argv",
        [str(SCRIPT), "https://docs.google.com/document/d/example/edit", str(tmp_path)],
    )
    monkeypatch.setattr(
        shooter, "connect_chrome", lambda: pytest.fail("Must not connect")
    )
    with pytest.raises(SystemExit) as error:
        shooter.main()
    assert error.value.code == 2
    assert marker.read_text() == '{"views": 9}'


@pytest.mark.parametrize(
    "args",
    [
        ["https://example.com/document/d/id/edit"],
        ["https://docs.google.com/document/d/id/edit", "--views", "0"],
        ["https://docs.google.com/document/d/id/edit", "--views", "501"],
    ],
)
def test_bad_arguments_never_connect(monkeypatch, tmp_path, args):
    monkeypatch.setattr("sys.argv", [str(SCRIPT), args[0], str(tmp_path), *args[1:]])
    monkeypatch.setattr(
        shooter, "connect_chrome", lambda: pytest.fail("Must not connect")
    )
    with pytest.raises(SystemExit) as error:
        shooter.main()
    assert error.value.code == 2
