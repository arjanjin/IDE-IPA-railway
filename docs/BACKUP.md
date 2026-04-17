# Backup & Restore — shared_kb (ChromaDB)

Quick reference for backing up and restoring the `shared_kb` collection on Railway.

## Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/backup/shared_kb` | GET | Export collection as JSON |
| `/restore/shared_kb` | POST | Import JSON back into collection |

Base URL: `https://ide-ipa-railway-production.up.railway.app`

Auth (if `MCP_AUTH_TOKENS` is set on Railway): add `Authorization: Bearer <token>` header.

---

## Backup

### PowerShell
```powershell
$ts = (Get-Date).ToString("yyyyMMdd_HHmmss", [System.Globalization.CultureInfo]::InvariantCulture)
curl -s "https://ide-ipa-railway-production.up.railway.app/backup/shared_kb" -o "backup_$ts.json"
python verify_backup.py "backup_$ts.json"
```

### Bash / Linux
```bash
ts=$(date +%Y%m%d_%H%M%S)
curl -s "https://ide-ipa-railway-production.up.railway.app/backup/shared_kb" -o "backup_${ts}.json"
python verify_backup.py "backup_${ts}.json"
```

### Success criteria
- HTTP 200
- File size > 50 KB
- `record_count > 0`
- Verify script shows expected types (`knowledge`, `lesson_atom`, `broadcast`, `risk_alert`)

---

## Restore

| Mode | Query string | Behavior |
|---|---|---|
| `merge` (default) | _(none)_ | Upsert records — preserves existing data |
| `replace` | `?mode=replace&confirm=true` | Delete collection first, then insert |

### Merge (safe, idempotent)
```powershell
curl -X POST "https://ide-ipa-railway-production.up.railway.app/restore/shared_kb" `
  -H "Content-Type: application/json" `
  --data-binary "@backup_FILENAME.json"
```

### Replace (destructive — wipes collection first)
```powershell
curl -X POST "https://ide-ipa-railway-production.up.railway.app/restore/shared_kb?mode=replace&confirm=true" `
  -H "Content-Type: application/json" `
  --data-binary "@backup_FILENAME.json"
```

### Success response
```json
{
  "restored": 35,
  "skipped": 0,
  "skipped_details": [],
  "mode": "merge",
  "total_docs": 35,
  "restored_at": "2026-04-17T..."
}
```

### Notes
- `replace` requires `confirm=true` — fails with 400 otherwise
- Original metadata (including `written_at`) is preserved exactly
- Embeddings are regenerated using the multilingual model on upsert
- Merge is idempotent — safe to re-run; running multiple backups in sequence is supported

---

## Emergency recovery (multiple backups)

When the collection is empty or partially lost and you have several backup snapshots from different times:

```powershell
# 1. Restore oldest backup (recovers original knowledge docs)
curl -X POST "https://ide-ipa-railway-production.up.railway.app/restore/shared_kb" `
  -H "Content-Type: application/json" --data-binary "@backup_OLDEST.json"

# 2. Restore newest backup (adds KB-generated docs created since then)
curl -X POST "https://ide-ipa-railway-production.up.railway.app/restore/shared_kb" `
  -H "Content-Type: application/json" --data-binary "@backup_NEWEST.json"

# 3. Verify final state
curl -s "https://ide-ipa-railway-production.up.railway.app/backup/shared_kb" -o restored_check.json
python verify_backup.py restored_check.json
```

Merge mode is idempotent — chaining multiple restores combines unique IDs and updates duplicates without creating extras.

---

## Verification script

`verify_backup.py` (in repo root):

```powershell
python verify_backup.py <backup_file.json>
```

Output shows:
- File path, record count, collection name, backup timestamp
- Counts by `type` metadata (knowledge / lesson_atom / broadcast / risk_alert)
- Counts by `source_agent`

---

## When to backup

| Trigger | Required |
|---|---|
| Before calling `l6_reset_shared_kb` | Yes |
| Before deploying code that touches DB | Yes |
| After significant coaching/portfolio updates | Recommended |
| Daily routine | Recommended (consider automation) |

---

## File handling

- Backup files match `backup*.json` and are gitignored automatically
- Store sensitive backups outside the repo or in encrypted form — they contain real portfolio data
- Suggested location: `D:\backups\kb\` (local) or cloud storage (Drive / S3)

---

## Implementation references

- Backup handler: [main.py:333](../main.py#L333) (`backup_shared_kb`)
- Restore handler: [main.py:387](../main.py#L387) (`restore_shared_kb`)
- Storage convention: see [project memory](../memory/project_kb_v1.md) — `type` metadata partitioning

---

## Known constraints

- `/backup/shared_kb` reads `chroma.sqlite3` directly — returns 404 if the file does not yet exist (e.g., immediately after a fresh container start with no prior write)
- Railway volume at `/data/chromadb` has been observed to reset during redeploys — keep recent backups outside the Railway environment
