# Batch-runner agent prompt (one agent per fixture batch)

You run a chain of edit tasks on ONE Google Doc copy and record each step. You never edit the
document yourself; each task is done by a fresh subagent that sees only its request.

Repo: /Users/alejo/best/work/tools/active/gdoc/cli (all `bin/…` paths below are under
`fidelity-tests/`). FIXTURE_DIR = fidelity-tests/<area>/v01. BATCH = 20260903-batch.
COPY_ID = <id>. ACCOUNT = alejandro.acelas-contractor@80000hours.org.
TASK ORDER: <slug1>, <slug2>, …

Step 0. Read FIXTURE_DIR/tasks.md once and extract the **Request** text of each slug in TASK
ORDER. Run `bin/gdt run-start FIXTURE_DIR <slug1> --copy-id COPY_ID --batch BATCH` (this
captures the before state; note the run_dir it prints). Also save the copy id:
`echo COPY_ID > FIXTURE_DIR/runs/BATCH/copy_id.txt`.

For each slug k in order:
1. `mkdir -p /private/tmp/claude-501/-Users-alejo-best-work-tools-active-gdoc-cli/42af5eae-5200-4240-a568-3a4515810a3e/scratchpad/batch-<area>-<slug>`
2. Spawn ONE subagent (Agent tool, subagent_type general-purpose) with EXACTLY this prompt,
   substituting SCRATCH_DIR, REQUEST (verbatim from tasks.md), URL
   (https://docs.google.com/document/d/COPY_ID/edit) and ACCOUNT — nothing else, no hints:

   ---
   First run: `cd SCRATCH_DIR && pwd` — that empty directory is your private working directory for everything. Do not read, list or write any file outside it. Do not use Read/Grep/Glob tools on the repository you may have been started in. Do not create copies of the document or any other Drive files.

   You have the `gdoc` CLI installed (`gdoc --help`, `gdoc <cmd> --help`). A colleague asks:

   "REQUEST"

   The document: URL

   Rules:
   - Always pass `--account ACCOUNT` after the subcommand (e.g. `gdoc cat --account ACCOUNT URL`).
   - Use only the gdoc CLI in Bash. Do not use a browser.
   - Do the request as a careful colleague would: read what you need, make the change, check it. If you believe the request cannot be done with the tools you have, say so and change nothing.

   When finished, report in exactly this shape:
   PWD: <output of pwd>
   COMMANDS: every gdoc command you ran, in order, one per line, with its one-line result
   WHAT I CHANGED: <plain description>
   SUCCEEDED: yes | partially | no — <one sentence>
   CONCERNS: <anything you noticed that might have gone wrong, or "none">
   ---

3. Wait for the subagent to finish. Save its report VERBATIM: write it to a temp file and run
   `bin/gdt-transcript <run_dir_k> < that_file` (this files transcript.md, captures the after
   state and runs the structural diff; it prints a `gate` line and an `expected=… unexpected=…`
   line — record both).
4. If there is a next slug: `bin/gdt run-start FIXTURE_DIR <slug k+1> --continue <run_dir_k>`
   and note the new run_dir.

After the last task: `bin/gdt batch-end FIXTURE_DIR BATCH`.

Rules: strictly sequential — never two subagents at once on this copy. Do not edit the doc,
tasks.md or any verdict yourself. If a subagent fails to report in the shape above, save
whatever it said. If a `gdt` command errors, stop and report the error.

Report back: one line per task `T<k> <slug> <run_dir> gate=<…> expected=<n> unexpected=<n>
SUCCEEDED=<what the subagent said>`, then any errors. Nothing else.
