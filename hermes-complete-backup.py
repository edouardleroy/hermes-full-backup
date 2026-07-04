#!/usr/bin/env python3
"""
Hermes Complete Backup — self-contained backup for disaster recovery.

Creates a ZIP archive with EVERYTHING needed to reinstall Hermes Agent
on a clean OS: config, credentials (SENSITIVE), skills, sessions, source
code, binary tools, and an install script.

USAGE:
    python hermes-complete-backup.py                          # Full backup
    python hermes-complete-backup.py -o /path/to/backup.zip   # Custom path
    python hermes-complete-backup.py --quick                  # Essentials only
    python hermes-complete-backup.py --json-config cfg.json   # External config
    python hermes-complete-backup.py --help                   # Full options

WARNING: This script backs up .env and auth.json (API keys, tokens).
Do NOT share the generated ZIP publicly.
"""

import os, sys, zipfile, argparse, json
from pathlib import Path
from datetime import datetime

_DEFAULT_HOME = (
    Path.home() / "AppData" / "Local" / "hermes"
    if sys.platform == "win32"
    else Path.home() / ".hermes"
)
HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(_DEFAULT_HOME)))
HERMES_SOURCE = HERMES_HOME / "hermes-agent"
BACKUP_DIR_DEFAULT = Path.home() / "hermes-backups"
INSTALL_BAT = next(
    (
        c for c in [
            Path(__file__).resolve().parent / "install.bat",
            Path(__file__).resolve().parent.parent / "install.bat",
        ] if c.exists()
    ), None
)

ESSENTIAL_FILES = [
    "config.yaml", ".env", "state.db", "auth.json", "auth.lock",
    "channel_directory.json", "discord_threads.json",
    "gateway_state.json", "gateway.lock", "gateway.pid",
    "processes.json", "SOUL.md", ".hermes_history",
]
ESSENTIAL_DIRS = ["cron", "memories", "kanban"]
EXCLUDE_SOURCE_DIRS = {
    "node_modules", ".git", "__pycache__", "venv", ".venv",
    "build", "dist", ".github", "docs", "website", "web",
    "nix", "docker", "packaging", "tui_gateway", "ui-tui",
    "apps", "optional-mcps", "optional-skills",
    "datagen-config-examples", "infographic", "locales", "assets",
}
EXCLUDE_SOURCE_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".webm",
}

class C:
    GREEN = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"
    CYAN = "\033[96m"; BOLD = "\033[1m"; RESET = "\033[0m"

def cprint(color, text, end="\n"):
    if sys.platform == "win32" and not os.environ.get("TERM"):
        print(text, end=end)
    else:
        print(f"{color}{text}{C.RESET}", end=end)

def add_file(zf, arcname, src):
    if not src.exists(): return False
    zf.write(str(src), arcname); return True

def add_dir(zf, prefix, src, exclude_dirs=None, exclude_exts=None):
    exclude_dirs = exclude_dirs or set()
    exclude_exts = exclude_exts or set()
    count = 0
    for root, dirs, files in os.walk(str(src)):
        rel = Path(root).relative_to(src)
        dirs[:] = [d for d in dirs if d not in exclude_dirs
                   and not any(p.startswith(".") for p in Path(rel, d).parts)]
        for f in files:
            if Path(f).suffix.lower() in exclude_exts or f.endswith(".pyc"):
                continue
            arc = f"{prefix}/{rel / f}" if str(rel) != "." else f"{prefix}/{f}"
            try:
                zf.write(str(Path(root) / f), arc); count += 1
            except (PermissionError, OSError): pass
    return count

def create_backup(output_path, quick=False):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with zipfile.ZipFile(str(output_path), "w", zipfile.ZIP_DEFLATED) as zf:
        # 1 - Config
        cprint(C.BOLD, "1/5  Configuration...")
        n = sum(1 for f in ESSENTIAL_FILES if add_file(zf, f, HERMES_HOME / f))
        for d in ESSENTIAL_DIRS:
            p = HERMES_HOME / d
            if p.exists(): n += add_dir(zf, d, p)
        sk = HERMES_HOME / "skills"
        if sk.exists(): n += add_dir(zf, "skills", sk)
        total += n; cprint(C.GREEN, f"    OK  {n} files")
        # 2 - Sessions / Logs
        if not quick:
            for d in ("sessions", "logs", "plugins", "profiles"):
                p = HERMES_HOME / d
                if p.exists():
                    c = add_dir(zf, d, p); total += c
                    cprint(C.GREEN, f"    OK  {c} files in {d}/")
        else:
            cprint(C.YELLOW, "    Skipped sessions/logs/plugins/profiles (--quick)")
        # 3 - Source
        cprint(C.BOLD, "\n2/5  Source code...")
        if HERMES_SOURCE.exists() and not quick:
            n = add_dir(zf, "hermes-agent", HERMES_SOURCE,
                        EXCLUDE_SOURCE_DIRS, EXCLUDE_SOURCE_EXTS)
            total += n; cprint(C.GREEN, f"    OK  {n} files")
        elif quick: cprint(C.YELLOW, "    Skipped (--quick)")
        else: cprint(C.YELLOW, f"    Not found at {HERMES_SOURCE}")
        # 4 - Binaries
        cprint(C.BOLD, "\n3/5  Binary tools...")
        n = 0
        for b in ("uv.exe", "uvw.exe", "uvx.exe"):
            p = HERMES_HOME / "bin" / b
            if p.exists(): zf.write(str(p), f"bin/{b}"); n += 1
        total += n; cprint(C.GREEN, f"    OK  {n} binaries")
        # 5 - Installer
        cprint(C.BOLD, "\n4/5  Install script...")
        if INSTALL_BAT: zf.write(str(INSTALL_BAT), "install.bat"); cprint(C.GREEN, "    install.bat included")
        else: cprint(C.YELLOW, "    install.bat not found (optional)")
        # README
        zf.writestr("LEEME.txt", _readme())
        cprint(C.GREEN, "    LEEME.txt included")
        size_mb = output_path.stat().st_size / (1024 * 1024)
        cprint(C.CYAN, f"\n{'='*60}")
        cprint(C.CYAN, f"  BACKUP COMPLETE: {output_path.name}")
        cprint(C.CYAN, f"  Size: {size_mb:.1f} MB  Files: {total}")
        cprint(C.CYAN, f"{'='*60}")
    return True

def _readme():
    return """\
============================================
  HERMES AGENT — COMPLETE BACKUP
  Disaster recovery archive
============================================

CONTENTS:
  config.yaml       — Configuration
  .env              — Credentials  (SENSITIVE)
  state.db          — Session history
  skills/           — Custom skills
  cron/             — Scheduled jobs
  memories/         — Persistent memory
  profiles/         — User profiles
  plugins/          — Installed plugins
  hermes-agent/     — Source code (reinstall on clean OS)
  bin/uv.exe        — Package manager
  install.bat       — One-click installer (Windows)

RESTORE:
  hermes import <backup.zip>
  Extract + run install.bat (clean Windows)

WARNING: Contains API keys from .env/auth.json.
Keep secure. Never upload publicly.
"""

def main():
    p = argparse.ArgumentParser(description="Hermes Complete Backup")
    p.add_argument("-o", "--output", help="Output .zip path")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--json-config", metavar="FILE")
    args = p.parse_args()
    if args.json_config:
        cfg = json.load(open(args.json_config))
        for k, v in cfg.items():
            g = globals()
            if k.upper() in g and k.upper() != "INSTALL_BAT": g[k.upper()] = Path(v)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = args.output or str(BACKUP_DIR_DEFAULT / f"hermes-full-{ts}.zip")
    print(f"  Output: {out}  Hermes home: {HERMES_HOME}")
    return 0 if create_backup(out, quick=args.quick) else 1

if __name__ == "__main__":
    try: sys.exit(main())
    except KeyboardInterrupt: print("\n  Interrupted."); sys.exit(130)
