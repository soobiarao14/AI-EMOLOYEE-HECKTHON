---
name: bronze-reasoning-loop
description: Process pending tasks in /Needs_Action — read content, reason about action needed, update status to completed, move to /Done, log activity. This is the "brain" that completes what the Watcher detected.
argument-hint: "[filename or --all]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# bronze-reasoning-loop

> **Watcher** detects tasks → **Reasoning Loop** processes them

## When to Use
- User says "process tasks", "run reasoning loop", "complete pending tasks"
- There are files in `/Needs_Action` with `status: pending`
- User asks to process a specific file from Needs_Action
- After watcher has moved files and they need to be acted on

## Architecture

```
Watcher (detect)          Reasoning Loop (process)
     │                           │
     │  filesystem_watcher.py    │  bronze-reasoning-loop skill
     │  polls /Inbox every 10s   │  reads /Needs_Action tasks
     │  wraps with metadata      │  reasons about each task
     │  routes to /Needs_Action  │  updates status → completed
     │                           │  moves to /Done
     ▼                           ▼
  /Needs_Action ──────────→ /Done
```

## Processing Pipeline

For each file in `/Needs_Action` with `status: pending`:

### Step 1: Discover
- Glob `/Needs_Action/*.md` to find all pending tasks
- If `$ARGUMENTS` is a specific filename, process only that file
- If `$ARGUMENTS` is `--all`, process everything pending

### Step 2: Read & Analyze
- Read the file content
- Extract YAML frontmatter: `type`, `original`, `detected`, `status`
- Read the `## Original Content` section to understand the task
- Check `Company_Handbook.md` for any applicable rules (payments > $100, sensitive info)

### Step 3: Reason
Based on the original content, determine:
- **What type of task is this?** (payment, communication, file operation, general)
- **Does it need human approval?** (check Handbook rules)
- **Can it be auto-completed?** (simple tasks without external actions)

If approval needed:
- Add `status: awaiting_approval` to frontmatter
- Add note in Action Log explaining why
- Do NOT move to Done — leave in Needs_Action
- Report to user

If auto-completable:
- Proceed to Step 4

### Step 4: Complete
1. Update YAML frontmatter: `status: pending` → `status: completed`
2. Add `completed: {timestamp}` to frontmatter
3. Add `processed_by: bronze-reasoning-loop` to frontmatter
4. Append to `## Action Log`:
   ```
   - [{timestamp}] Processed by reasoning loop: {summary of action taken}
   - [{timestamp}] Status changed: pending → completed
   - [{timestamp}] Moved from /Needs_Action to /Done
   ```

### Step 5: Move to Done
1. Write updated content to `/Done/{filename}`
2. Delete original from `/Needs_Action`

### Step 6: Update Dashboard
1. Count files in all folders
2. Update Dashboard.md counts and timestamp
3. Add row to Recent Activity table:
   ```
   | {time} | 🧠 Reasoning Loop | Processed `{filename}` → /Done |
   ```

### Step 7: Report
Tell user what was processed:
- How many files processed
- Which ones needed approval (left in Needs_Action)
- Which ones were completed (moved to Done)
- Updated counts

## Handbook Compliance Rules

Before completing any task, check:

| Content Pattern | Action |
|----------------|--------|
| Contains "pay", "payment", "$" + amount > 100 | Flag for approval |
| Contains "send", "email", "message" to external | Flag for approval |
| Contains "delete", "remove" on shared files | Flag for approval |
| General/internal tasks | Auto-complete |

## Examples

### "Process all pending tasks"
```
→ Glob Needs_Action/*.md
→ Found 3 files with status: pending
→ File 1: tpy_processed.md — empty task, auto-complete → Done
→ File 2: invoice_processed.md — contains "$500 payment" → awaiting_approval
→ File 3: notes_processed.md — general notes, auto-complete → Done
→ Report: 2 completed, 1 needs approval
→ Dashboard updated
```

### "Process invoice_processed.md"
```
→ Read Needs_Action/invoice_processed.md
→ Content mentions payment $500 → exceeds $100 threshold
→ Status set to awaiting_approval
→ Report: "This task requires human approval (payment > $100)"
```

### "Run reasoning loop"
```
→ Same as "Process all pending tasks"
```
