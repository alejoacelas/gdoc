#!/usr/bin/env bash
# Rebuild gdt-write-v01: a tab whose terminal empty paragraph carries a bullet.
# Usage: build.sh   (reads account from fidelity-tests/config.yaml; prints DOC and TAB ids)
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd); cfg="$here/../../config.yaml"
A=$(grep -E '^account:' "$cfg" | sed 's/^account:[[:space:]]*//;s/[[:space:]]*#.*//')
DOC=$(gdoc new --account "$A" --json "gdt-write-v01" | python3 -c "import sys,json;print(json.loads([l for l in sys.stdin if l.startswith('{')][0])['id'])")
gdoc cat --account "$A" "$DOC" >/dev/null
TAB=$(gdoc add-tab --account "$A" "$DOC" "Repro" | grep -oE '^t\.[a-z0-9]+' | tail -1)
for _ in 1 2 3; do gdoc cat --account "$A" "$DOC" >/dev/null; gdoc write --account "$A" --tab "$TAB" "$DOC" "$here/seed.md" && break; done
gdoc structure --account "$A" --tab "$TAB" "$DOC" > /tmp/gdt-write-v01.json
python3 - "$DOC" "$TAB" "$A" <<'PY'
import json, sys
doc, tab, account = sys.argv[1:4]
from gdoc.util import set_active_account; set_active_account(account)
from gdoc.api.docs import get_docs_service
paras = [c for c in json.load(open("/tmp/gdt-write-v01.json"))["tab"]["documentTab"]["body"]["content"] if "paragraph" in c]
last = paras[-1]   # the empty terminal paragraph
get_docs_service().documents().batchUpdate(documentId=doc, body={"requests": [{"createParagraphBullets": {
    "range": {"startIndex": last["startIndex"], "endIndex": last["endIndex"], "tabId": tab},
    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}}]}).execute()
PY
echo "DOC=$DOC TAB=$TAB"
echo "repro: gdoc write --account $A --tab $TAB $DOC $here/rewrite.md && gdoc pull --account $A $DOC out.md"
