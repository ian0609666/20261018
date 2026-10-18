"""Command-line interface for OSS Maintainer Audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .audit import AuditReport, audit_repository


def _percentage(report: AuditReport) -> int:
    if report.maximum_score == 0:
        return 0
    return round(report.score * 100 / report.maximum_score)


def render_text(report: AuditReport) -> str:
    lines = [
        f"Repository: {report.root}",
        f"Maintenance score: {report.score}/{report.maximum_score} "
        f"({_percentage(report)}%) - {report.rating}",
        "",
    ]

    for check in report.checks:
        status = "PASS" if check.passed else "MISS"
        detail = f" ({', '.join(check.matches)})" if check.matches else ""
        lines.append(f"[{status}] {check.label} [{check.weight}]{detail}")
        if not check.passed:
            lines.append(f"       Next: {check.recommendation}")

    if report.missing:
        lines.extend(
            [
                "",
                f"Next step: address {len(report.missing)} missing maintenance item(s).",
            ]
        )
    else:
        lines.extend(["", "All configured maintenance checks passed."])

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-maintainer-audit",
        description="Audit an open-source repository's maintenance readiness.",
    )
    subparsers = parser.add_subparsers(dest="command")
    audit_parser = subparsers.add_parser("audit", help="Audit a repository")
    audit_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository directory (default: current directory)",
    )
    audit_parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON",
    )
    audit_parser.add_argument(
        "--fail-under",
        type=int,
        default=0,
        metavar="SCORE",
        help="Exit with status 1 when the score is below SCORE (0-100)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if not 0 <= args.fail_under <= 100:
        parser.error("--fail-under must be between 0 and 100")

    try:
        report = audit_repository(args.path)
    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(render_text(report))

    return 1 if _percentage(report) < args.fail_under else 0
