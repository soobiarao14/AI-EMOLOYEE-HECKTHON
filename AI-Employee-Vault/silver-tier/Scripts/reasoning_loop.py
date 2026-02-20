"""
Bronze Tier - Reasoning Loop v1.0
Processes pending tasks in /Needs_Action:
  - Reads content + YAML frontmatter
  - Checks Company_Handbook rules (payments, sensitive actions)
  - Auto-completes or flags for approval
  - Moves completed tasks to /Done
  - Updates Dashboard.md counts + activity
  - Logs to /Logs/reasoning.log
"""

from pathlib import Path
from datetime import datetime
import argparse
import logging
import re
import sys

# ── Config ────────────────────────────────────────────────────────────────────
DEFAULT_VAULT = r"E:\Personal-AI-Employee-Hackathon-0\AI-Employee-Vault\bronze-tier"

VAULT_PATH: Path
NEEDS_ACTION: Path
DONE: Path
INBOX: Path
LOGS: Path
LOG_FILE: Path

logger = logging.getLogger("reasoning-loop")


# ── Colored Console Formatter ─────────────────────────────────────────────────
class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG:    "\033[2m",
        logging.INFO:     "\033[96m",
        logging.WARNING:  "\033[93m",
        logging.ERROR:    "\033[91m",
        logging.CRITICAL: "\033[1;91m",
    }
    RESET = "\033[0m"
    DIM = "\033[2m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        ts = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        return f"{self.DIM}[{ts}]{self.RESET} {color}{record.getMessage()}{self.RESET}"


def setup_logging() -> None:
    logger.setLevel(logging.DEBUG)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    console.setFormatter(ColorFormatter())
    logger.addHandler(console)

    try:
        LOGS.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(fh)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")


# ── Helpers ───────────────────────────────────────────────────────────────────
def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_short() -> str:
    return datetime.now().strftime("%H:%M")


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter as a dict."""
    fm = {}
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if match:
        for line in match.group(1).strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                fm[key.strip()] = val.strip()
    return fm


def update_frontmatter(content: str, updates: dict) -> str:
    """Update or add keys in YAML frontmatter."""
    match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
    if not match:
        return content

    fm_text = match.group(2)

    for key, val in updates.items():
        pattern = rf"^{re.escape(key)}:.*$"
        if re.search(pattern, fm_text, re.MULTILINE):
            fm_text = re.sub(pattern, f"{key}: {val}", fm_text, flags=re.MULTILINE)
        else:
            fm_text += f"\n{key}: {val}"

    return match.group(1) + fm_text + match.group(3) + content[match.end():]


def append_action_log(content: str, entry: str) -> str:
    """Append an entry to the ## Action Log section."""
    timestamp = now_str()
    log_line = f"- [{timestamp}] {entry}"

    if "## Action Log" in content:
        content = content.replace(
            "## Action Log",
            f"## Action Log\n{log_line}",
            1
        )
    else:
        content += f"\n## Action Log\n{log_line}\n"
    return content


# ── Handbook Compliance Check ─────────────────────────────────────────────────
APPROVAL_PATTERNS = [
    (r"\$\s*(\d+)", "payment_amount"),       # Dollar amounts
    (r"(?i)\b(pay|payment|invoice)\b", "payment_keyword"),
    (r"(?i)\b(send|email|message|notify)\b", "external_comms"),
    (r"(?i)\b(delete|remove|drop)\b", "destructive_action"),
]


def check_needs_approval(content: str) -> tuple[bool, str]:
    """Check content against Handbook rules. Returns (needs_approval, reason)."""
    # Check for payment amounts > $100
    amounts = re.findall(r"\$\s*(\d+(?:\.\d+)?)", content)
    for amt_str in amounts:
        try:
            if float(amt_str) > 100:
                return True, f"Payment amount ${amt_str} exceeds $100 threshold"
        except ValueError:
            pass

    # Check for external communication keywords
    if re.search(r"(?i)\b(send|email|message)\b.*\b(external|client|vendor|outside)\b", content):
        return True, "Contains external communication — requires first-time approval"

    # Check for destructive actions on shared files
    if re.search(r"(?i)\b(delete|remove)\b.*\b(shared|team|production)\b", content):
        return True, "Destructive action on shared resource"

    return False, ""


# ── Core Processing ───────────────────────────────────────────────────────────
def get_pending_tasks(target: str = None) -> list[Path]:
    """Find pending tasks in /Needs_Action."""
    tasks = []
    try:
        for f in sorted(NEEDS_ACTION.iterdir()):
            if not f.is_file() or f.suffix != ".md":
                continue
            if target and f.name != target:
                continue

            content = f.read_text(encoding="utf-8")
            fm = parse_frontmatter(content)

            if fm.get("status") == "pending":
                tasks.append(f)
    except FileNotFoundError:
        logger.error(f"Needs_Action folder not found: {NEEDS_ACTION}")
    except PermissionError:
        logger.error(f"Permission denied reading: {NEEDS_ACTION}")

    return tasks


def process_task(task_path: Path) -> str:
    """Process a single task. Returns: 'completed', 'approval_needed', or 'error'."""
    try:
        content = task_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Cannot read {task_path.name}: {e}")
        return "error"

    fm = parse_frontmatter(content)
    logger.info(f"  Processing: {task_path.name} (original: {fm.get('original', 'unknown')})")

    # Step 1: Check handbook compliance
    needs_approval, reason = check_needs_approval(content)

    if needs_approval:
        logger.warning(f"  APPROVAL NEEDED: {reason}")
        content = update_frontmatter(content, {"status": "awaiting_approval"})
        content = append_action_log(content, f"Flagged for approval: {reason}")

        try:
            task_path.write_text(content, encoding="utf-8")
        except Exception as e:
            logger.error(f"Cannot update {task_path.name}: {e}")
            return "error"

        return "approval_needed"

    # Step 2: Auto-complete
    timestamp = now_str()
    content = update_frontmatter(content, {
        "status": "completed",
        "completed": timestamp,
        "processed_by": "bronze-reasoning-loop",
    })
    content = append_action_log(content, "Processed by reasoning loop — auto-completed")
    content = append_action_log(content, "Status changed: pending → completed")
    content = append_action_log(content, "Moved from /Needs_Action to /Done")

    # Step 3: Write to Done
    dest = DONE / task_path.name
    counter = 1
    while dest.exists():
        dest = DONE / f"{task_path.stem}_{counter}.md"
        counter += 1

    try:
        dest.write_text(content, encoding="utf-8")
        logger.info(f"  >> {task_path.name} --> /Done/{dest.name}")
    except Exception as e:
        logger.error(f"Cannot write to Done: {e}")
        return "error"

    # Step 4: Delete from Needs_Action
    try:
        task_path.unlink()
    except Exception as e:
        logger.error(f"Cannot delete {task_path.name}: {e}")
        return "error"

    return "completed"


def update_dashboard(completed: list[str], flagged: list[str]) -> None:
    """Update Dashboard.md with counts and activity."""
    dashboard = VAULT_PATH / "Dashboard.md"
    if not dashboard.exists():
        logger.warning("Dashboard.md not found")
        return

    try:
        inbox_count = sum(1 for f in INBOX.iterdir() if f.is_file())
        action_count = sum(1 for f in NEEDS_ACTION.iterdir() if f.is_file())
        done_count = sum(1 for f in DONE.iterdir() if f.is_file())
    except OSError as e:
        logger.error(f"Error counting folders: {e}")
        return

    try:
        content = dashboard.read_text(encoding="utf-8")
        timestamp = now_str()
        short = now_short()

        # Update counts
        content = re.sub(r"(🕐 Last updated \| ).+", f"\\g<1>{timestamp} |", content)
        content = re.sub(r"(📥 Inbox items \| )\d+", f"\\g<1>{inbox_count}", content)
        content = re.sub(r"(⚡ Needs_Action items \| )\d+", f"\\g<1>{action_count}", content)
        content = re.sub(r"(✅ Done items \| )\d+", f"\\g<1>{done_count}", content)
        content = re.sub(r"(📥 `/Inbox` \| )\d+", f"\\g<1>{inbox_count}", content)
        content = re.sub(r"(⚡ `/Needs_Action` \| )\d+", f"\\g<1>{action_count}", content)
        content = re.sub(r"(✅ `/Done` \| )\d+", f"\\g<1>{done_count}", content)

        # Add activity rows
        divider = "|------|--------|---------|"
        new_rows = []
        for name in completed:
            new_rows.append(f"| {short} | 🧠 Reasoning Loop | `{name}` processed → /Done |")
        for name in flagged:
            new_rows.append(f"| {short} | ⚠️ Needs Approval | `{name}` flagged — awaiting human review |")

        if new_rows and divider in content:
            insert = divider + "\n" + "\n".join(new_rows)
            content = content.replace(divider, insert, 1)

        dashboard.write_text(content, encoding="utf-8")
        logger.info(f"  Dashboard updated: Inbox={inbox_count} | Action={action_count} | Done={done_count}")
    except Exception as e:
        logger.error(f"Failed updating Dashboard: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────
def run_reasoning_loop(target: str = None) -> None:
    """Run the reasoning loop on pending tasks."""
    logger.info("=" * 55)
    logger.info("  BRONZE TIER - REASONING LOOP v1.0")
    logger.info("=" * 55)
    logger.info(f"  Vault:  {VAULT_PATH}")
    logger.info(f"  Source: {NEEDS_ACTION}")
    logger.info(f"  Target: {DONE}")
    logger.info("=" * 55)

    tasks = get_pending_tasks(target)

    if not tasks:
        logger.info("No pending tasks in /Needs_Action")
        return

    logger.info(f"Found {len(tasks)} pending task(s)")

    completed = []
    flagged = []
    errors = []

    for task in tasks:
        result = process_task(task)
        if result == "completed":
            completed.append(task.name)
        elif result == "approval_needed":
            flagged.append(task.name)
        else:
            errors.append(task.name)

    # Update dashboard
    update_dashboard(completed, flagged)

    # Summary
    logger.info("=" * 55)
    logger.info("  REASONING LOOP COMPLETE")
    logger.info(f"  Completed:      {len(completed)}")
    logger.info(f"  Needs Approval: {len(flagged)}")
    logger.info(f"  Errors:         {len(errors)}")
    logger.info("=" * 55)

    if completed:
        logger.info(f"  Done: {', '.join(completed)}")
    if flagged:
        logger.warning(f"  Flagged: {', '.join(flagged)}")
    if errors:
        logger.error(f"  Failed: {', '.join(errors)}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bronze Tier Reasoning Loop — processes pending tasks from /Needs_Action"
    )
    parser.add_argument(
        "--vault", type=str, default=DEFAULT_VAULT,
        help=f"Path to vault root (default: {DEFAULT_VAULT})"
    )
    parser.add_argument(
        "--file", type=str, default=None,
        help="Process a specific file (e.g. --file tpy_processed.md)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    VAULT_PATH = Path(args.vault)
    INBOX = VAULT_PATH / "Inbox"
    NEEDS_ACTION = VAULT_PATH / "Needs_Action"
    DONE = VAULT_PATH / "Done"
    LOGS = VAULT_PATH / "Logs"
    LOG_FILE = LOGS / "reasoning.log"

    setup_logging()
    run_reasoning_loop(target=args.file)
