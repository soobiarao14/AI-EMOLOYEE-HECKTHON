"""
Bronze Tier - Filesystem Watcher v3.0
Monitors /Inbox for new files every 10 seconds.
Uses Python logging module → console (colored) + /Logs/watcher.log (append).
On detection: wraps file with metadata → /Needs_Action, appends activity to Dashboard.md.
"""

from pathlib import Path
from datetime import datetime
import argparse
import logging
import re
import sys
import time

# ── Config ────────────────────────────────────────────────────────────────────
DEFAULT_VAULT = r"E:\Personal-AI-Employee-Hackathon-0\AI-Employee-Vault\bronze-tier"
POLL_INTERVAL = 10  # seconds

processed_files: set[str] = set()

# Globals — set after arg parse
VAULT_PATH: Path
INBOX: Path
NEEDS_ACTION: Path
DONE: Path
LOGS: Path
LOG_FILE: Path

logger = logging.getLogger("watcher")


# ── Colored Console Formatter ─────────────────────────────────────────────────
class ColorFormatter(logging.Formatter):
    """ANSI-colored formatter for console output."""
    COLORS = {
        logging.DEBUG:    "\033[2m",       # dim
        logging.INFO:     "\033[96m",      # cyan
        logging.WARNING:  "\033[93m",      # yellow
        logging.ERROR:    "\033[91m",      # red
        logging.CRITICAL: "\033[1;91m",    # bold red
    }
    RESET = "\033[0m"
    DIM = "\033[2m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        return f"{self.DIM}[{timestamp}]{self.RESET} {color}{record.getMessage()}{self.RESET}"


def setup_logging() -> None:
    """Configure dual logging: colored console + plain-text file."""
    logger.setLevel(logging.DEBUG)

    # Console handler — colored
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    console.setFormatter(ColorFormatter())
    logger.addHandler(console)

    # File handler — plain text, append mode
    try:
        LOGS.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")


# ── Helpers ───────────────────────────────────────────────────────────────────
def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_short() -> str:
    return datetime.now().strftime("%H:%M")


# ── Core Functions ────────────────────────────────────────────────────────────
def wrap_with_metadata(source: Path) -> str:
    """Read original content and wrap in .md metadata envelope."""
    timestamp = now_str()

    try:
        full_content = source.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning(f"Binary file detected: {source.name}, storing as reference")
        full_content = f"[Binary or unreadable file: {source.name}]"
    except PermissionError:
        logger.error(f"Permission denied reading: {source.name}")
        full_content = f"[Permission denied: {source.name}]"

    preview = full_content[:200]
    if len(full_content) > 200:
        preview += "\n... (truncated)"

    return f"""---
type: dropped_file
original: {source.name}
detected: {timestamp}
status: pending
---

# Task: {source.stem}

## Original Content
{preview}

## Full Content
{full_content}

## Action Log
- [{timestamp}] Detected in /Inbox by Watcher, processed to /Needs_Action
"""


def scan_inbox() -> list[Path]:
    """Return new (unprocessed) files in /Inbox, ignoring system files."""
    skip = {".DS_Store", ".gitkeep", "desktop.ini", "Thumbs.db"}
    new_files = []
    try:
        for item in INBOX.iterdir():
            if item.is_file() and item.name not in processed_files and item.name not in skip:
                new_files.append(item)
    except PermissionError:
        logger.error(f"Permission denied scanning: {INBOX}")
    except FileNotFoundError:
        logger.error(f"Inbox folder missing: {INBOX}")
    return new_files


def process_file(source: Path) -> None:
    """Wrap file with metadata → /Needs_Action, delete from Inbox."""
    dest_name = f"{source.stem}_processed.md"
    dest = NEEDS_ACTION / dest_name

    # Avoid overwriting
    counter = 1
    while dest.exists():
        dest = NEEDS_ACTION / f"{source.stem}_processed_{counter}.md"
        counter += 1

    try:
        wrapped = wrap_with_metadata(source)
        dest.write_text(wrapped, encoding="utf-8")
        logger.info(f"  >> {source.name} --> /Needs_Action/{dest.name}")
    except PermissionError:
        logger.error(f"Cannot write to {dest} — permission denied")
        return
    except OSError as e:
        logger.error(f"Failed writing {dest}: {e}")
        return

    try:
        source.unlink()
        processed_files.add(source.name)
    except PermissionError:
        logger.error(f"Cannot delete source {source.name} — permission denied, file was copied but not removed")
    except OSError as e:
        logger.error(f"Failed deleting {source.name}: {e}")

    # Append activity line to Dashboard
    append_dashboard_activity(source.name, dest.name)


def append_dashboard_activity(original: str, dest: str) -> None:
    """Append a detection line to Dashboard.md Recent Activity section."""
    dashboard = VAULT_PATH / "Dashboard.md"
    if not dashboard.exists():
        logger.warning("Dashboard.md not found, skipping activity append")
        return

    try:
        content = dashboard.read_text(encoding="utf-8")
        timestamp = now_short()
        new_line = f"| {timestamp} | 📥 Watcher Detect | `{original}` → `/Needs_Action/{dest}` |"

        # Insert after the Recent Activity table header row
        marker = "| Time | Action | Details |"
        divider = "|------|--------|---------|"

        if marker in content and divider in content:
            content = content.replace(
                divider,
                f"{divider}\n{new_line}",
                1
            )
        else:
            # Fallback: append to end of file
            content += f"\n- [{timestamp}] New file detected: {original} → Needs_Action/{dest}\n"

        dashboard.write_text(content, encoding="utf-8")
        logger.info(f"  Dashboard activity appended for {original}")
    except Exception as e:
        logger.error(f"Failed updating Dashboard.md: {e}")


def update_dashboard_counts() -> None:
    """Recount files in each folder and update Dashboard.md stats."""
    dashboard = VAULT_PATH / "Dashboard.md"
    if not dashboard.exists():
        logger.warning("Dashboard.md not found, skipping count update")
        return

    try:
        inbox_count = sum(1 for f in INBOX.iterdir() if f.is_file())
        action_count = sum(1 for f in NEEDS_ACTION.iterdir() if f.is_file())
        done_count = sum(1 for f in DONE.iterdir() if f.is_file())
    except OSError as e:
        logger.error(f"Error counting folder contents: {e}")
        return

    try:
        content = dashboard.read_text(encoding="utf-8")
        timestamp = now_str()

        # Update status table
        content = re.sub(r"(🕐 Last updated \| ).+", f"\\g<1>{timestamp} |", content)
        content = re.sub(r"(📥 Inbox items \| )\d+", f"\\g<1>{inbox_count}", content)
        content = re.sub(r"(⚡ Needs_Action items \| )\d+", f"\\g<1>{action_count}", content)
        content = re.sub(r"(✅ Done items \| )\d+", f"\\g<1>{done_count}", content)

        # Update folder overview table
        content = re.sub(r"(📥 `/Inbox` \| )\d+", f"\\g<1>{inbox_count}", content)
        content = re.sub(r"(⚡ `/Needs_Action` \| )\d+", f"\\g<1>{action_count}", content)
        content = re.sub(r"(✅ `/Done` \| )\d+", f"\\g<1>{done_count}", content)

        dashboard.write_text(content, encoding="utf-8")
        logger.info(f"  Counts updated: Inbox={inbox_count} | Action={action_count} | Done={done_count}")
    except Exception as e:
        logger.error(f"Failed updating Dashboard counts: {e}")


# ── Main Loop ─────────────────────────────────────────────────────────────────
def print_banner() -> None:
    logger.info("=" * 55)
    logger.info("  BRONZE TIER - FILESYSTEM WATCHER v3.0")
    logger.info("=" * 55)
    logger.info(f"  Vault:    {VAULT_PATH}")
    logger.info(f"  Monitor:  {INBOX}")
    logger.info(f"  Target:   {NEEDS_ACTION}")
    logger.info(f"  Log file: {LOG_FILE}")
    logger.info(f"  Interval: {POLL_INTERVAL}s")
    logger.info("=" * 55)
    logger.info("  Drop any file in /Inbox — watcher will pick it up!")
    logger.warning("  Press Ctrl+C to stop")
    logger.info("=" * 55)


def run_watcher() -> None:
    """Main polling loop with full error handling."""
    print_banner()

    # Ensure all folders exist
    for folder in [INBOX, NEEDS_ACTION, DONE, LOGS]:
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.critical(f"Cannot create folder {folder}: {e}")
            sys.exit(1)

    cycle = 0
    while True:
        try:
            cycle += 1
            new_files = scan_inbox()

            if new_files:
                logger.info(f"[Cycle {cycle}] Found {len(new_files)} new file(s)!")
                for f in sorted(new_files, key=lambda p: p.name):
                    process_file(f)
                update_dashboard_counts()
            else:
                if cycle % 6 == 0:
                    logger.debug(f"[Cycle {cycle}] Inbox empty, watching...")

        except KeyboardInterrupt:
            logger.warning("Watcher stopped by user (Ctrl+C)")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error in cycle {cycle}: {e}", exc_info=True)

        time.sleep(POLL_INTERVAL)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bronze Tier Filesystem Watcher v3.0 — monitors /Inbox and routes to /Needs_Action"
    )
    parser.add_argument(
        "--vault", type=str, default=DEFAULT_VAULT,
        help=f"Path to Obsidian vault root (default: {DEFAULT_VAULT})"
    )
    parser.add_argument(
        "--interval", type=int, default=POLL_INTERVAL,
        help=f"Poll interval in seconds (default: {POLL_INTERVAL})"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    VAULT_PATH = Path(args.vault)
    INBOX = VAULT_PATH / "Inbox"
    NEEDS_ACTION = VAULT_PATH / "Needs_Action"
    DONE = VAULT_PATH / "Done"
    LOGS = VAULT_PATH / "Logs"
    LOG_FILE = LOGS / "watcher.log"
    POLL_INTERVAL = args.interval

    setup_logging()
    run_watcher()
