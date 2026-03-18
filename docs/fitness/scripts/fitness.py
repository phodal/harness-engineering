#!/usr/bin/env python3
"""
Fitness Function Runner

Scans docs/fitness/*.md files, parses YAML frontmatter,
executes metrics commands, and prints a unified report.

Usage:
    python3 docs/fitness/scripts/fitness.py [OPTIONS]

Options:
    --dry-run       Show what would be executed without running
    --verbose       Show command output on failure
    --tier TIER     Run only metrics up to the specified tier (fast|normal|deep)
    --help          Show this help message
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FITNESS_DIR = Path(__file__).resolve().parents[1]
TIER_ORDER = {"fast": 0, "normal": 1, "deep": 2}


def parse_frontmatter(content: str) -> dict | None:
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    return yaml.safe_load(match.group(1))


def should_run_metric(metric: dict, default_tier: str, tier_filter: Optional[str]) -> bool:
    if tier_filter is None:
        return True

    metric_tier = metric.get("tier", default_tier)
    return TIER_ORDER.get(metric_tier, 1) <= TIER_ORDER.get(tier_filter, 1)


def run_metric(metric: dict, default_tier: str, dry_run: bool, verbose: bool) -> tuple[str, bool, str, str]:
    name = metric.get("name", "unknown")
    command = metric.get("command", "")
    pattern = metric.get("pattern")
    tier = metric.get("tier", default_tier)

    if dry_run:
        return name, True, f"[DRY-RUN] Would run: {command}", tier

    try:
        result = subprocess.run(
            ["/bin/bash", "-lc", command],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=PROJECT_ROOT,
        )
    except subprocess.TimeoutExpired:
        return name, False, "TIMEOUT (300s)", tier
    except Exception as exc:
        return name, False, str(exc), tier

    output = (result.stdout or "") + (result.stderr or "")
    passed = bool(re.search(pattern, output, re.IGNORECASE)) if pattern else result.returncode == 0

    max_len = 2000 if verbose else 500
    return name, passed, output[:max_len], tier


def print_help() -> None:
    print(__doc__)
    sys.exit(0)


def parse_tier(argv: list[str]) -> Optional[str]:
    for index, arg in enumerate(argv):
        if arg == "--tier" and index + 1 < len(argv):
            tier = argv[index + 1]
            if tier not in TIER_ORDER:
                print(f"Error: invalid tier '{tier}'. Must be one of: fast, normal, deep.")
                sys.exit(1)
            return tier
    return None


def main() -> None:
    if "--help" in sys.argv:
        print_help()

    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv
    tier_filter = parse_tier(sys.argv)

    print("=" * 60)
    print("FITNESS FUNCTION REPORT")
    if dry_run:
        print("(DRY-RUN MODE)")
    if tier_filter:
        print(f"(TIER: {tier_filter.upper()})")
    print("=" * 60)

    total_score = 0.0
    total_weight = 0
    hard_gate_failed: list[str] = []

    for md_file in sorted(FITNESS_DIR.glob("*.md")):
        if md_file.name in {"README.md", "REVIEW.md"}:
            continue

        frontmatter = parse_frontmatter(md_file.read_text())
        if not frontmatter or "metrics" not in frontmatter:
            continue

        dimension = frontmatter.get("dimension", "unknown")
        weight = int(frontmatter.get("weight", 0))
        default_tier = frontmatter.get("tier", "normal")
        metrics = [
            metric
            for metric in frontmatter.get("metrics", [])
            if should_run_metric(metric, default_tier, tier_filter)
        ]

        if not metrics:
            continue

        print(f"\n## {dimension.upper()} (weight: {weight}%)")
        print(f"   Source: {md_file.name}")

        dim_passed = 0
        dim_total = 0

        for metric in metrics:
            name, passed, output, tier = run_metric(metric, default_tier, dry_run, verbose)
            status = "✅ PASS" if passed else "❌ FAIL"
            hard_gate = " [HARD GATE]" if metric.get("hard_gate") else ""
            tier_label = f" [{tier}]" if tier_filter else ""

            print(f"   - {name}: {status}{hard_gate}{tier_label}")

            if not passed and (verbose or metric.get("hard_gate")):
                print(f"     Command: {metric.get('command', '')}")
                if output and output != "TIMEOUT (300s)":
                    for line in output.strip().split("\n")[:10]:
                        print(f"     > {line}")
                    if output.count("\n") > 10:
                        print(f"     > ... ({output.count(chr(10)) - 10} more lines)")

            if not passed and metric.get("hard_gate"):
                hard_gate_failed.append(name)

            dim_passed += 1 if passed else 0
            dim_total += 1

        if dim_total:
            dim_score = (dim_passed / dim_total) * 100
            total_score += dim_score * weight
            total_weight += weight
            print(f"   Score: {dim_score:.0f}%")

    print("\n" + "=" * 60)

    if hard_gate_failed:
        print(f"❌ HARD GATES FAILED: {', '.join(hard_gate_failed)}")
        print("   Cannot proceed until hard gates pass.")
        sys.exit(2)

    if total_weight > 0:
        final_score = total_score / total_weight
        print(f"FINAL SCORE: {final_score:.1f}%")

        if final_score >= 90:
            print("✅ PASS")
        elif final_score >= 80:
            print("⚠️  WARN - Consider improvements")
        else:
            print("❌ BLOCK - Score too low")
            sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()
