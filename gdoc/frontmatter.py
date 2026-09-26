"""Simple YAML frontmatter parser (no pyyaml dependency)."""

import re

_FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from content.

    Returns (metadata_dict, body_without_frontmatter).
    If no valid frontmatter, returns ({}, content).
    Only supports flat key: value pairs.

    A leading `---\\n...\\n---\\n` block is only treated as frontmatter
    when at least one `key: value` line parses out of it. Empty blocks
    or blocks containing only prose (for example, a thematic break
    followed by another `---`) are left in place to avoid silently
    eating content.
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}, content

    raw = match.group(1)
    metadata: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        colon = line.find(":")
        if colon == -1:
            continue
        key = line[:colon].strip()
        value = line[colon + 1 :].strip()
        if key:
            metadata[key] = value

    if not metadata:
        return {}, content

    body = content[match.end() :]
    return metadata, body


def add_frontmatter(body: str, metadata: dict) -> str:
    """Prepend YAML frontmatter to body.

    Args:
        body: The document body.
        metadata: Flat dict of key-value pairs.

    Returns:
        Content with frontmatter prepended.

    Values are flattened to a single line: a line break in a value
    (e.g. a doc title) would otherwise inject arbitrary frontmatter
    keys. splitlines() covers the same separator set parse_frontmatter
    splits on (\\n, \\r, \\x0b, \\u2028, ...), unlike a [\\r\\n] regex.
    """
    lines = ["---"]
    for key, value in metadata.items():
        value = " ".join(str(value).splitlines())
        lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + body


def update_frontmatter_value(content: str, key: str, value: str) -> str:
    """Update one flat field without reserializing unrelated frontmatter."""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return content
    raw = match[1]
    replacement = f"{key}: {' '.join(str(value).splitlines())}"
    pattern = re.compile(r"^" + re.escape(key) + r":[^\r\n]*(?=\r?$)", re.MULTILINE)
    raw = (
        pattern.sub(lambda _: replacement, raw)
        if pattern.search(raw)
        else raw + ("\r\n" if "\r\n" in content else "\n") + replacement
    )
    return content[: match.start(1)] + raw + content[match.end(1) :]


def preserve_and_replace(
    path: str, content: str, *, expected: str | None = None
) -> bool:
    """Publish a file without discarding any concurrently edited inode.

    Move the previous inode to a retained recovery file before publishing with
    exclusive hard-link creation. Editors with an already-open descriptor keep
    writing to that recovery file; editors saving a new inode at the original
    path win the race. This is recovery-backed publication, not filesystem CAS.
    """
    import os
    import sys
    import tempfile
    from pathlib import Path
    from uuid import uuid4

    target = Path(path)
    if expected is not None and read_local_text(target) != expected:
        print(f"WARN: local file changed; left {path} untouched", file=sys.stderr)
        return False
    fd, staging = tempfile.mkstemp(prefix=".gdoc-publish-", dir=target.parent)
    backup = target.with_name(target.name + ".gdoc-backup-" + uuid4().hex)
    moved = False
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if target.exists():
            os.chmod(staging, target.stat().st_mode & 0o777)
            os.rename(target, backup)
            moved = True
            print(f"LOCAL: previous file retained at {backup}", file=sys.stderr)
            if expected is not None and read_local_text(backup) != expected:
                try:
                    os.link(backup, target)
                except FileExistsError:
                    pass
                print("WARN: local file changed; replacement skipped", file=sys.stderr)
                return False
        try:
            os.link(staging, target)
        except FileExistsError:
            print(
                f"WARN: concurrent local save at {path}; replacement skipped",
                file=sys.stderr,
            )
            return False
        return True
    except Exception:
        if moved and not target.exists():
            try:
                os.link(backup, target)
            except FileExistsError:
                pass
        raise
    finally:
        os.unlink(staging)


def body_fingerprint(body: str) -> str:
    """Identify exactly the local body last pulled or acknowledged."""
    import hashlib

    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def read_local_text(path) -> str:
    """Read source bytes as UTF-8 without normalizing frontmatter newlines."""
    with open(path, encoding="utf-8", newline="") as stream:
        return stream.read()
