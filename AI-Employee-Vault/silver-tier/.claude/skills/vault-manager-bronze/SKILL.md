---
name: vault-manager-bronze
description: Bronze Tier vault management - folder checks, file moves between Inbox/Needs_Action/Done, Dashboard counts update
argument-hint: "[action] [filename]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# vault-manager-bronze

## When to Use
- Jab vault folders manage karne hon (Inbox, Needs_Action, Done)
- Files move karne hon ek folder se doosre mein
- Dashboard refresh karna ho with accurate counts
- Naye files ka triage karna ho from Inbox
- Company Handbook rules check karne hon before any action

## Vault Config
- **Root**: `E:\Personal-AI-Employee-Hackathon-0\AI-Employee-Vault\bronze-tier`
- **WSL**: `/mnt/e/Personal-AI-Employee-Hackathon-0/AI-Employee-Vault/bronze-tier`
- **Folders**: `/Inbox`, `/Needs_Action`, `/Done`, `/Logs`

## Core Instructions

### Count Files in Folders
1. Use Glob to count `.md` files in each folder (ignore `.DS_Store`, `.gitkeep`, non-md):
   - `Inbox/*.md`
   - `Needs_Action/*.md`
   - `Done/*.md`
2. Report counts to user

### Update Dashboard.md
After ANY file operation:
1. Count files in all folders (see above)
2. Read `Dashboard.md`
3. Edit these fields with real values:
   - `Inbox items: {count}`
   - `Needs_Action items: {count}`
   - `Done items: {count}`
   - `Last updated: {YYYY-MM-DD HH:MM}`
4. Add entry under `## Recent Activity` describing what happened
5. Confirm to user

### Move File Between Folders
When user says "move X from A to B":
1. Verify source exists: Glob `{from_folder}/{filename}`
2. Read the source file content
3. Append action log to content:
   ```
   ## Action Log
   - [YYYY-MM-DD HH:MM] Moved from /{source} to /{dest}
   ```
4. Write updated content to `{to_folder}/{filename}`
5. Delete original: `rm "{source_path}"`
6. Update Dashboard.md counts (see above)
7. Log in Recent Activity

### Triage Inbox
1. List all `.md` files in `/Inbox`
2. Show each file's title (first `#` heading or filename)
3. Ask user: move to Needs_Action or Done?
4. Execute moves
5. Update Dashboard

### Check Handbook Before Actions
Before any external or sensitive action:
1. Read `Company_Handbook.md`
2. Verify: payment < $100? recipient verified? tone professional?
3. Proceed only if rules pass

## Examples

### "Update dashboard counts"
→ Glob count all 3 folders → Edit Dashboard.md with real counts → Done

### "Move report.md from Needs_Action to Done"
→ Read file → Append log → Write to /Done → Delete from /Needs_Action → Update Dashboard

### "Triage inbox"
→ List /Inbox files → Ask user per file → Move → Update Dashboard

### "Move any .txt from Needs_Action to Done"
→ Glob `Needs_Action/*.txt` → If found: move each → If none: report "No .txt files found" → Update Dashboard
