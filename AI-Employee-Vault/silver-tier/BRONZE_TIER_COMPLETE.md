---
title: Bronze Tier - Personal AI Employee
status: COMPLETE
date: 2026-02-16
tier: Bronze (Minimum Viable Deliverable)
---

# 🏆 Bronze Tier — Submission Document

> **Personal AI Employee Hackathon** | Built with Claude Code + Obsidian Vault

---

## ✅ Requirements Checklist

### Vault Structure & Core Files
- [x] Obsidian vault initialized at `E:\Personal-AI-Employee-Hackathon-0\AI-Employee-Vault\bronze-tier`
- [x] `/Inbox` folder — drop zone for new tasks
- [x] `/Needs_Action` folder — active work queue
- [x] `/Done` folder — completed task archive
- [x] `/Logs` folder — watcher activity logs
- [x] `/Scripts` folder — automation scripts
- [x] `Dashboard.md` — live stats with emoji tables, folder counts, activity log, quick links
- [x] `Company_Handbook.md` — approval rules, communication style, error handling, preferences

### Claude Code Read/Write Access
- [x] Create files in any vault folder
- [x] Read file contents back
- [x] Move files between folders (Inbox → Needs_Action → Done)
- [x] Edit files in-place (Dashboard count updates via regex)
- [x] Delete files after processing
- [x] All operations tested and verified on 2026-02-16

### One Working Watcher Script
- [x] `Scripts/filesystem_watcher.py` (v3.0) — polls `/Inbox` every 10 seconds
- [x] Python `logging` module — INFO for detections, ERROR for issues
- [x] Dual output: colored console (ANSI) + `/Logs/watcher.log` (append mode)
- [x] YAML metadata wrapping: `type`, `original`, `detected`, `status` frontmatter
- [x] Original content preview (first 200 chars) + full content preserved
- [x] Auto-appends activity row to Dashboard.md Recent Activity table
- [x] Auto-updates folder counts in Dashboard after every detection
- [x] 14 try/except blocks covering every file operation
- [x] CLI args: `--vault`, `--interval` for flexible deployment
- [x] Pure Python stdlib — zero external dependencies

### All AI Functionality as Agent Skills
- [x] `.claude/skills/vault-manager-bronze/SKILL.md` — auto-discovered by Claude Code
- [x] YAML frontmatter: name, description, argument-hint, allowed-tools
- [x] 5 core operations: count files, update dashboard, move files, triage inbox, check handbook
- [x] 4 documented examples with step-by-step action sequences
- [x] Live tested: dashboard refresh, file moves, simulation of edge cases

---

## 📁 Final Vault Structure

```
bronze-tier/
├── .claude/
│   └── skills/
│       └── vault-manager-bronze/
│           └── SKILL.md              ← Agent Skill definition
├── Inbox/                            ← Drop zone (watcher monitors this)
├── Needs_Action/                     ← Active work queue
├── Done/                             ← Completed tasks
│   ├── test-file.md
│   └── TEST_BRONZE.md
├── Logs/                             ← Watcher writes watcher.log here
├── Scripts/
│   └── filesystem_watcher.py         ← Watcher v3.0
├── Dashboard.md                      ← Live stats dashboard
├── Company_Handbook.md               ← Rules of engagement
├── BRONZE_COMPLETE.md                ← Quick completion note
├── BRONZE_STATUS.md                  ← Status audit checklist
└── BRONZE_TIER_COMPLETE.md           ← This file (submission doc)
```

---

## 🎬 Step-by-Step Demo Flow

### Step 1: Start the Watcher

**PowerShell (Windows):**
```powershell
# Foreground (see colored logs live)
python "E:\Personal-AI-Employee-Hackathon-0\AI-Employee-Vault\bronze-tier\Scripts\filesystem_watcher.py"

# Background (hidden window)
Start-Process python -ArgumentList '"E:\Personal-AI-Employee-Hackathon-0\AI-Employee-Vault\bronze-tier\Scripts\filesystem_watcher.py"' -WindowStyle Hidden

# Check logs anytime
Get-Content "E:\Personal-AI-Employee-Hackathon-0\AI-Employee-Vault\bronze-tier\Logs\watcher.log" -Tail 20
```

**WSL / Linux:**
```bash
# Foreground
python3 /mnt/e/Personal-AI-Employee-Hackathon-0/AI-Employee-Vault/bronze-tier/Scripts/filesystem_watcher.py

# Background
nohup python3 /mnt/e/Personal-AI-Employee-Hackathon-0/AI-Employee-Vault/bronze-tier/Scripts/filesystem_watcher.py > /dev/null 2>&1 &

# Tail logs
tail -f /mnt/e/Personal-AI-Employee-Hackathon-0/AI-Employee-Vault/bronze-tier/Logs/watcher.log
```

### Step 2: Start Claude Code

```bash
cd /mnt/e/Personal-AI-Employee-Hackathon-0/AI-Employee-Vault/bronze-tier
claude
```

Claude auto-discovers `vault-manager-bronze` skill on startup.

### Step 3: Drop a File into Inbox

```bash
echo "Pay vendor $50 for office supplies" > /mnt/e/Personal-AI-Employee-Hackathon-0/AI-Employee-Vault/bronze-tier/Inbox/pay_vendor.txt
```

### Step 4: Watch It Process (within 10 seconds)

Watcher console output:
```
[2026-02-16 18:05:10] [Cycle 5] Found 1 new file(s)!
[2026-02-16 18:05:10]   >> pay_vendor.txt --> /Needs_Action/pay_vendor_processed.md
[2026-02-16 18:05:10]   Dashboard activity appended for pay_vendor.txt
[2026-02-16 18:05:10]   Counts updated: Inbox=0 | Action=1 | Done=2
```

### Step 5: Ask Claude to Process It

In Claude Code session:
```
"Move pay_vendor_processed.md from Needs_Action to Done"
```

Claude follows vault-manager-bronze skill instructions:
1. Reads file from `/Needs_Action`
2. Appends action log entry
3. Writes to `/Done`
4. Deletes from `/Needs_Action`
5. Updates Dashboard counts

### Step 6: Verify in Obsidian

Open vault in Obsidian → Dashboard.md shows updated counts and activity log.

---

## 🧩 Component Summary

| Component | File | What It Does |
|-----------|------|-------------|
| 📊 Dashboard | `Dashboard.md` | Live folder counts, activity table, component status, quick links |
| 📖 Handbook | `Company_Handbook.md` | Approval rules, communication style, error handling, preferences |
| 👁️ Watcher | `Scripts/filesystem_watcher.py` | Polls Inbox → wraps with metadata → routes to Needs_Action → logs |
| 🛠️ Agent Skill | `.claude/skills/vault-manager-bronze/SKILL.md` | File moves, count updates, triage, handbook compliance checks |
| 📥→⚡→✅ Pipeline | `/Inbox` → `/Needs_Action` → `/Done` | Full task lifecycle with audit trail |

---

## 📝 Lessons Learned

1. **Start with the file system, not the AI.** Getting the vault structure, watcher, and file operations solid first meant Claude Code had a reliable foundation to build on. The AI skill layer was easy to add once the plumbing worked.

2. **Agent Skills are just well-structured prompts.** The `SKILL.md` file isn't magic — it's a clear set of instructions with examples that Claude follows. The key is being specific about the exact steps (Glob → Read → Edit → Write) rather than vague ("update the dashboard").

3. **Logging saves debugging time.** Moving from `print()` to the `logging` module with dual output (console + file) made it trivial to diagnose issues. The watcher.log file persists across runs, giving a complete audit trail.

---

*Bronze Tier completed on 2026-02-16 | Built with Claude Code (Opus 4.6) + Python 3.12 + Obsidian*
