"""
Script to check and verify authoritative healthcare knowledge sources.
Reports availability, versions, local cache paths, and credentials status.
Usage:
    python scripts/check_knowledge_sources.py
"""

import os
import sys
from tabulate import tabulate

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from resources.resource_manager import ResourceManager


def main():
    print(f"\n{'='*80}")
    print(f"KNOWLEDGE RESOURCE MANAGER (SECTION 17) — HEALTHCARE SOURCE STATUS")
    print(f"{'='*80}")

    mgr = ResourceManager()
    manifests = mgr.get_all_manifests()

    table_rows = []
    for key, res in manifests.items():
        table_rows.append([
            res.name,
            res.version,
            res.availability,
            res.resource_type,
            "YES" if res.credentials_required else "NO",
            res.details,
        ])

    print(tabulate(
        table_rows,
        headers=["Source", "Version", "Availability", "Distribution Type", "Auth Required?", "Verification Details"],
        tablefmt="github"
    ))

    print(f"\n{'='*80}")
    print("STATUS SUMMARY:")
    for key, res in manifests.items():
        status_line = f"{res.name:12} {res.availability}"
        print(f"  {status_line}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
