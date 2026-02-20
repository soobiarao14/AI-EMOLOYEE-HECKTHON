# 🤖 AI Employee Dashboard — Bronze Tier

> [!tip] 🏆 **Personal AI Employee** | Hackathon Project | Powered by Claude Code

---

## 🌟 Project Overview

**Personal AI Employee** is an autonomous task-processing system built inside an Obsidian vault. It watches for incoming files, reasons about their content, takes action, and archives results — all without manual intervention.

| 🏷️ Detail           | 💡 Value                      |
| -------------------- | ----------------------------- |
| 🚀 Project           | Personal AI Employee          |
| 🥉 Current Tier      | Bronze — **✅ COMPLETE**       |
| 🏗️ Architecture     | Obsidian Vault + Claude Code  |
| ⚙️ Automation Engine | File Watcher + Reasoning Loop |

---

## 📊 Task Counters

> [!abstract] Live folder counts — synced to real files on disk

| 📂 Folder            | 🔢 Count |
| -------------------- | -------: |
| 📥 Inbox items       |        0 |
| ⚡ Needs_Action items |        0 |
| ✅ Done items         |        2 |

> *Counts are updated each time the `vault-manager-bronze` skill runs or the reasoning loop completes a cycle.*

---

## 🔄 Workflow

```mermaid
graph LR
    A["📥 Inbox"] -->|"🔍 Watcher detects<br>every 10s"| B["⚡ Needs_Action"]
    B -->|"🧠 Reasoning Loop<br>reads & completes"| C["✅ Done"]

    style A fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
    style B fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:2px
    style C fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
```

**Step-by-step:**

1. 📥 **Inbox** — Drop any `.txt` or `.md` file here.
2. 👁️ **Watcher** picks it up within 10 seconds, wraps it with YAML front-matter, and moves it to `Needs_Action`.
3. 🧠 **Reasoning Loop** reads the file, determines the required action, updates its status to completed, and moves it to `Done`.
4. 📊 **Dashboard** counters and activity log are updated automatically.

---

## 📋 Recent Activity

> [!info] 🕐 Latest actions performed by the AI Employee

| 🕐 Time | 🎬 Action           | 📝 Details                                                    |
|---------|---------------------|---------------------------------------------------------------|
| 00:00   | 🔄 Dashboard Refresh | Counts synced to real folder state (0/0/2)                   |
| 23:54   | 🧠 Reasoning Loop    | `actionss_processed.md` processed and moved to Done          |
| 23:52   | 👁️ Watcher Detect    | `actionss.txt` picked up and moved to Needs_Action           |
| 23:01   | 📦 File Moved        | `test_task.md` moved Needs_Action → Done via vault-manager   |
| 22:54   | 🧠 Reasoning Loop    | `tyt_processed.md` processed and moved to Done               |
| 22:53   | 👁️ Watcher Detect    | `tyt.txt` picked up and moved to Needs_Action                |
| 22:26   | 🧠 Reasoning Loop    | `rose_processed.md` processed and moved to Done              |
| 22:25   | 👁️ Watcher Detect    | `rose.txt` picked up and moved to Needs_Action               |
| 22:24   | 🧠 Reasoning Loop    | `clintes_processed.md` processed and moved to Done           |
| 22:24   | 🧠 Reasoning Loop    | `king_processed.md` processed and moved to Done              |
| 22:24   | 🧠 Reasoning Loop    | `typn_processed.md` processed and moved to Done              |

> *📁 Older entries are available in `Logs/reasoning.log` and `Logs/watcher.log`.*

---

## 🔗 Quick Links

> [!example] 🗂️ Navigate the vault

| 📎 Resource                                      | 📖 Description                        |
| ------------------------------------------------ | ------------------------------------- |
| 📥 [[Inbox\|Inbox]]                              | Drop zone for new tasks               |
| ⚡ [[Needs_Action\|Needs_Action]]                 | Tasks currently being processed       |
| ✅ [[Done\|Done]]                                 | Completed and archived tasks          |
| 📜 [[Logs\|Logs]]                                | Watcher and reasoning loop logs       |
| 📘 [[README\|README]]                            | Project readme and setup instructions |
| 📕 [[Company_Handbook\|Company Handbook]]        | Rules of engagement and compliance    |
| ✔️ [[BRONZE_COMPLETE\|Bronze Checklist]]         | Final checklist and demo flow         |
| 📊 [[BRONZE_STATUS\|Bronze Status]]              | Status audit with pass/fail table     |
| 🏅 [[BRONZE_TIER_COMPLETE\|Bronze Deliverables]] | Detailed deliverable list             |

---

## 🖥️ System Status

> [!success] All systems operational

| 🔧 Component             | 📄 Details                                    | 🚦 Status           |
|--------------------------|-----------------------------------------------|---------------------|
| 👁️ File Watcher          | `Scripts/filesystem_watcher.py` — 10s polling | 🟢 Ready            |
| 🧠 Reasoning Loop        | `bronze-reasoning-loop` skill                 | 🟢 Ready            |
| 🗂️ Vault Manager         | `vault-manager-bronze` skill                  | 🟢 Loaded           |
| 📕 Company Handbook      | `Company_Handbook.md`                         | 🟢 Active           |
| 🕐 Last Dashboard Update | `2026-02-17 00:00`                            | ⬜ —                |

---

> [!tip] 💡 **Pro Tip:** Drop any file into `/Inbox` while the watcher is running. It will be picked up within 10 seconds, wrapped with YAML metadata, and moved to `/Needs_Action` automatically.

---

<p align="center">
  🤖 <em>Dashboard auto-updated by <code>vault-manager-bronze</code> agent skill</em> 🤖
</p>

- [01:59] New file detected: clients_notes.txt → Needs_Action/clients_notes_processed.md

- [02:03] New file detected: clients_notes.txt → Needs_Action/clients_notes_processed.md

- [02:08] New file detected: clients_notes.txt → Needs_Action/clients_notes_processed.md

- [02:51] New file detected: clients_notes.txt → Needs_Action/clients_notes_processed.md

- [15:21] New file detected: test_budget.txt → Needs_Action/test_budget_processed.md

- [15:23] New file detected: pay_vendor.txt → Needs_Action/pay_vendor_processed.md

- [15:23] New file detected: pay_vendor2.txt → Needs_Action/pay_vendor2_processed.md
