# Personal AI Employee — Bronze Tier

Local-first AI agent using **Obsidian vault** + **Claude Code**. No cloud APIs, no databases — just files, folders, and a watcher script.

---

## What It Does

```
You drop a file in /Inbox
     ↓
Watcher detects it (10s polling)
     ↓
Wraps with YAML metadata → /Needs_Action
     ↓
Claude processes it via Agent Skill
     ↓
Moves to /Done with action log
     ↓
Dashboard.md auto-updates counts
```

---

## Project Structure

```
bronze-tier/
├── Inbox/                → Drop zone (watcher monitors this)
├── Needs_Action/         → Active work queue
├── Done/                 → Completed tasks
├── Logs/                 → watcher.log lives here
├── Scripts/
│   └── filesystem_watcher.py   → Watcher v3.0
├── .claude/skills/
│   └── vault-manager-bronze/
│       └── SKILL.md            → Agent Skill definition
├── Dashboard.md          → Live stats + activity log
├── Company_Handbook.md   → Rules of engagement
└── README.md             → This file
```

---

## Quick Start

### 1. Start the Watcher

```bash
# Windows PowerShell
python "E:\Personal-AI-Employee-Hackathon-0\AI-Employee-Vault\bronze-tier\Scripts\filesystem_watcher.py"

# WSL / Linux
python3 /mnt/e/Personal-AI-Employee-Hackathon-0/AI-Employee-Vault/bronze-tier/Scripts/filesystem_watcher.py
```

### 2. Start Claude Code

```bash
cd /mnt/e/Personal-AI-Employee-Hackathon-0/AI-Employee-Vault/bronze-tier
claude
```

### 3. Drop a Test File

```bash
echo "Review Q1 budget report" > Inbox/review_budget.txt
```

Within 10 seconds:
- Watcher picks it up
- Creates `review_budget_processed.md` in `/Needs_Action` with metadata
- Updates Dashboard.md counts
- Logs to `/Logs/watcher.log`

### 4. Ask Claude to Complete It

```
"Move review_budget_processed.md from Needs_Action to Done"
```

---

## Components

| Component | Purpose |
|-----------|---------|
| `filesystem_watcher.py` | Polls `/Inbox` every 10s, wraps files with YAML metadata, routes to `/Needs_Action` |
| `vault-manager-bronze` | Claude Code Agent Skill — file moves, dashboard updates, triage, handbook checks |
| `Dashboard.md` | Live folder counts, activity table, component status |
| `Company_Handbook.md` | Approval rules, communication style, error handling, preferences |

---

## Tech Stack

- **Python 3.12** — stdlib only, zero dependencies
- **Claude Code** (Opus 4.6) — Agent Skills for vault management
- **Obsidian** — markdown vault with wikilinks
- **Platform** — Windows 11 + WSL2

---

## Requirements

- Python 3.10+
- Claude Code CLI (`claude`)
- Obsidian (for viewing, optional for functionality)

---

## License

Hackathon project — built for the Personal AI Employee challenge.
