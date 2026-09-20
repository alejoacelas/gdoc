# gdoc fidelity decisions

## Core decisions

### Preserve native regressions

- [Retain anonymous native reproductions alongside request tests](#fidelity).
- [Keep the terminal-bullet defect visible until the writer is fixed](#bullet-repro).
- [Group nested items in one bullet request](#nested-lists).

### Capture comparable evidence

- [Use a dedicated authenticated browser for reproducible captures](#capture).
- [Do not substitute PDF evidence for interactive Docs features](#pdf-limits).

### Protect suggestion semantics

- [Never let suggest silently become a direct edit](#suggest-gate).

## Details

<a id="fidelity"></a>
### Retain anonymous native reproductions alongside request tests

The offline suite checks request planning; the fidelity suite checks real Google Docs results. Preserve frozen anonymous structures and minimal scripted repros for failures found in private documents, without committing the private source snapshots. Keep the class-level [test catalogue](docs/TESTS.md) as a navigation aid, not a current live pass-rate guarantee. See [repro index](fidelity-tests/repros.md) and `8762094`.

<a id="bullet-repro"></a>
### Keep the terminal-bullet defect visible until the writer is fixed

The terminal empty paragraph can retain a UI-created bullet after body deletion, causing newly inserted text to inherit that list. The retained [regression](tests/test_write_tab_terminal_bullet.py) deliberately fails until the writer clears the surviving bullet and indents before insertion. This checkout's writer still lacks that reset; the later reconstruction branch's fix must not be claimed here. The plain-tail control prevents unnecessary bullet-clearing requests. See [tab writer](gdoc/api/docs.py) and `8762094`.

<a id="nested-lists"></a>
### Group nested items in one bullet request

Emit one createParagraphBullets range per list block, with children sharing the parent's range. Per-paragraph requests normalize every item to nesting level zero. Keep style requests ahead of bullet creation and account for indentation tabs that earlier blocks remove. A bullet child under a numbered parent uses the parent's numbered preset because the API cannot nest across two presets; this is an intentional representational limit. See [request builder](gdoc/mdparse.py), [nested-list tests](tests/test_write_tab_nested_list.py), and `91ce59f`.

<a id="capture"></a>
### Use a dedicated authenticated browser for reproducible captures

The historically named headless shooter uses normal off-screen Chrome, a dedicated profile and human login. Refuse attachment if the debugging port belongs to a different profile. Fixed viewport/scroll geometry and saved timings make captures comparable, while the existing filing format keeps evidence usable by the fidelity tools. The script captures the rendered UI rather than inferring document content from the DOM. See [capture script](fidelity-tests/bin/gdt-shot-headless), [capture tests](fidelity-tests/tests/test_shot_headless.py), and `9a115e8`.

<a id="pdf-limits"></a>
### Do not substitute PDF evidence for interactive Docs features

PDF comparison can support claims about visible text, line breaks, bullets and footnotes in the captured cases. The saved benchmark did not establish fidelity for comments, suggestions or chips, so faster PDF exports are not evidence for those behaviours. Preserve browser captures and native structures when the claim depends on review objects or other interactive content. See [capture tooling](fidelity-tests/bin/gdt-shot-headless), [test catalogue](docs/TESTS.md), and `9a115e8`.

<a id="suggest-gate"></a>
### Never let suggest silently become a direct edit

Require the non-mutating Developer Preview gate, a source revision, no overlap with existing suggestions, and successful saved-state/ID readback. Unsupported structural suggestions refuse before mutation; they do not fall back to edit. Keep the selected account and credential identity stable across the read, gate and write. These checks exist because an unenrolled backend was observed treating the requested suggestion mode as a direct edit. See [suggestion API](gdoc/api/docs.py), [suggestion tests](tests/test_suggest.py), and [account tests](tests/test_account_context.py).
