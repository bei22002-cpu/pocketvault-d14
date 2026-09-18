#!/usr/bin/env python3
"""Embed CAD part manifests into designs.js for offline gallery use."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
index = json.loads((root / "models" / "INDEX.json").read_text(encoding="utf-8"))
parts_by_id = {m["id"]: m["parts"] for m in index["models"]}

js_path = root / "designs.js"
text = js_path.read_text(encoding="utf-8")

for did, parts in parts_by_id.items():
    marker = f'id: "{did}"'
    idx = text.find(marker)
    if idx < 0:
        print("missing", did)
        continue
    chunk = text[idx : idx + 900]
    if "cadParts:" in chunk:
        print("skip", did)
        continue
    img_m = re.search(r'image:\s*"[^"]+",', chunk)
    if not img_m:
        print("no image", did)
        continue
    insert_at = idx + img_m.end()
    injection = "\n    cadParts: " + json.dumps(parts, ensure_ascii=False) + ","
    text = text[:insert_at] + injection + text[insert_at:]
    print("injected", did)

js_path.write_text(text, encoding="utf-8")
print("wrote", js_path)
