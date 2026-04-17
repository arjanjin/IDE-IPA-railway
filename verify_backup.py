"""Verify a shared_kb backup JSON file. Usage: python verify_backup.py <backup_file>"""
import json
import sys
from collections import Counter

fn = sys.argv[1] if len(sys.argv) > 1 else "backup.json"
with open(fn, encoding="utf-8") as f:
    d = json.load(f)

print(f"file:       {fn}")
print(f"records:    {d['record_count']}")
print(f"collection: {d['collection']['name']}")
print(f"timestamp:  {d['backup_timestamp']}")

types = Counter()
agents = Counter()
for r in d["records"]:
    m = r.get("metadata") or {}
    types[m.get("type", "knowledge")] += 1
    agents[m.get("source_agent", "?")] += 1

print(f"by type:    {dict(types)}")
print("by agent:")
for k, v in agents.most_common():
    print(f"  {k}: {v}")
