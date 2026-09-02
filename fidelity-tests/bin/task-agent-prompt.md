# Task-agent prompt template (agent track)

Spawn with the Agent tool from an EMPTY working directory (cd into a fresh scratch dir
first). Substitute REQUEST, URL, ACCOUNT. Nothing else is passed.

---
You have the `gdoc` CLI installed (`gdoc --help`, `gdoc <cmd> --help`). A colleague asks:

"REQUEST"

The document: URL

Rules:
- Always pass `--account ACCOUNT` after the subcommand (e.g. `gdoc cat --account ACCOUNT URL`).
- Use only the gdoc CLI in Bash. Do not use a browser, and do not read or write any file
  outside your current working directory (`pwd`), which is empty scratch space for you.
- Do the request as a careful colleague would: read what you need, make the change, check
  it. If you believe the request cannot be done with the tools you have, say so and change
  nothing.

When finished, report in exactly this shape:
PWD: <output of pwd>
COMMANDS: every gdoc command you ran, in order, one per line, with its one-line result
WHAT I CHANGED: <plain description>
SUCCEEDED: yes | partially | no — <one sentence>
CONCERNS: <anything you noticed that might have gone wrong, or "none">
---
