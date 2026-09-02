# Known gdoc behaviours that affect fidelity runs

Each entry links to a repro line or an issue. Delete entries that have neither, and
entries whose issue is closed once a rerun confirms the fix.

| Behaviour | Evidence |
|---|---|
| `gdoc edit` parses the replacement as markdown: a leading `1. ` or `# ` restyles the whole paragraph; `_word_` becomes italic. Use `--old-file/--new-file`. | [LucaDeLeo/gdoc#57](https://github.com/LucaDeLeo/gdoc/issues/57) |
| `gdoc edit` rewrites the whole paragraph's runs, so strikethrough, highlight, bold or italic elsewhere in the paragraph can be lost. | `fidelity-tests/repros.md#kitchen-sink-v01-edit-strips-paragraph-styles` |
| `gdoc write` from markdown misplaces paragraph styles after emoji and other non-BMP characters; looks like Python length versus UTF-16 index arithmetic. | needs repro |
| `gdoc cat` refuses `--tab` with `--comments`; use `gdoc comments --all`. | needs repro |
| Revision export ignores `--tab`. | needs repro |

Operational, not defects:

- The default account may not see the fixtures; always pass `--account` from
  `config.yaml`.
