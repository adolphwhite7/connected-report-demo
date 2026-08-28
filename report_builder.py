"""Build a connected Markdown report from selected structured findings."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import quote, urlparse


@dataclass(frozen=True)
class Finding:
    finding_id: str
    title: str
    theme: str
    summary: str
    evidence: tuple[str, ...]
    recommended_action: str
    source_label: str
    source_url: str


def _required_text(record: dict[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{field}' must be a non-empty string")
    return value.strip()


def _validate_source_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Source URL must use http or https and include a host")


def _parse_finding(record: Any) -> Finding:
    if not isinstance(record, dict):
        raise ValueError("Every finding must be a JSON object")

    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("Field 'evidence' must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in evidence):
        raise ValueError("Every evidence item must be a non-empty string")

    source = record.get("source")
    if not isinstance(source, dict):
        raise ValueError("Field 'source' must be an object")
    source_label = _required_text(source, "label")
    source_url = _required_text(source, "url")
    _validate_source_url(source_url)

    return Finding(
        finding_id=_required_text(record, "id"),
        title=_required_text(record, "title"),
        theme=_required_text(record, "theme"),
        summary=_required_text(record, "summary"),
        evidence=tuple(item.strip() for item in evidence),
        recommended_action=_required_text(record, "recommended_action"),
        source_label=source_label,
        source_url=source_url,
    )


def load_findings(path: Path) -> list[Finding]:
    """Load and validate findings from a JSON file."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read valid JSON from {path}: {exc}") from exc

    records = payload.get("findings") if isinstance(payload, dict) else None
    if not isinstance(records, list) or not records:
        raise ValueError("Input must contain a non-empty 'findings' list")

    findings = [_parse_finding(record) for record in records]
    seen: set[str] = set()
    duplicates: set[str] = set()
    for finding in findings:
        if finding.finding_id in seen:
            duplicates.add(finding.finding_id)
        seen.add(finding.finding_id)
    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise ValueError(f"Duplicate finding IDs: {duplicate_list}")
    return findings


def select_findings(findings: Iterable[Finding], selected_ids: Sequence[str]) -> list[Finding]:
    """Return findings in the caller's requested order."""
    by_id = {finding.finding_id: finding for finding in findings}
    unknown = [finding_id for finding_id in selected_ids if finding_id not in by_id]
    if unknown:
        raise ValueError(f"Unknown finding IDs: {', '.join(unknown)}")
    if not selected_ids:
        raise ValueError("Select at least one finding ID")
    seen_selection: set[str] = set()
    duplicates: list[str] = []
    for finding_id in selected_ids:
        if finding_id in seen_selection and finding_id not in duplicates:
            duplicates.append(finding_id)
        seen_selection.add(finding_id)
    if duplicates:
        raise ValueError(f"Select each finding ID once: {', '.join(duplicates)}")
    return [by_id[finding_id] for finding_id in selected_ids]


def _join_words(values: Sequence[str]) -> str:
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return f"{', '.join(values[:-1])}, and {values[-1]}"


def _escape_label(value: str) -> str:
    return value.replace("[", "\\[").replace("]", "\\]")


def _escape_url(value: str) -> str:
    return quote(value, safe=":/?#[]@!$&'*+,;=%")


def build_report(report_title: str, findings: Sequence[Finding]) -> str:
    """Render a deterministic connected report in Markdown."""
    if not report_title.strip():
        raise ValueError("Report title must not be empty")
    if not findings:
        raise ValueError("At least one finding is required")

    themes = list(dict.fromkeys(finding.theme for finding in findings))
    by_theme: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        by_theme[finding.theme].append(finding)

    lines = [
        f"# {report_title.strip()}",
        "",
        "## Executive Summary",
        "",
        (
            f"This report connects {len(findings)} selected findings across "
            f"{len(themes)} theme{'s' if len(themes) != 1 else ''}: "
            f"{_join_words(themes)}."
        ),
        "",
        "Together, the findings support this practical sequence:",
        "",
    ]
    lines.extend(
        f"{index}. {finding.recommended_action.rstrip('.')}"
        for index, finding in enumerate(findings, start=1)
    )

    lines.extend(["", "## How the Findings Connect", ""])
    for theme in themes:
        members = by_theme[theme]
        ids = _join_words([finding.finding_id for finding in members])
        if len(members) > 1:
            lines.append(
                f"- **{theme}:** {ids} identify related parts of the same operating issue; "
                "reviewing them together prevents one fix from leaving the other cause in place."
            )
        else:
            lines.append(
                f"- **{theme}:** {ids} adds a distinct constraint that should be addressed "
                "alongside the other selected findings."
            )

    lines.extend(["", "## Selected Findings", ""])
    for finding in findings:
        lines.extend(
            [
                f"### {finding.finding_id} — {finding.title}",
                "",
                f"**Theme:** {finding.theme}",
                "",
                finding.summary,
                "",
                "**Evidence**",
                "",
                *[f"- {item}" for item in finding.evidence],
                "",
                f"**Recommended action:** {finding.recommended_action}",
                "",
                f"**Source:** [{_escape_label(finding.source_label)}]({_escape_url(finding.source_url)})",
                "",
            ]
        )

    lines.extend(
        [
            "## Selection Record",
            "",
            "Included finding IDs: " + ", ".join(f.finding_id for f in findings),
            "",
        ]
    )
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Combine selected structured findings into one Markdown report."
    )
    parser.add_argument("--input", type=Path, required=True, help="JSON findings file")
    parser.add_argument("--select", nargs="+", required=True, metavar="ID")
    parser.add_argument("--output", type=Path, help="Write Markdown to this path")
    parser.add_argument(
        "--title", default="Connected Operations Review", help="Report heading"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        findings = load_findings(args.input)
        selected = select_findings(findings, args.select)
        report = build_report(args.title, selected)
        if args.output:
            args.output.write_text(report, encoding="utf-8")
        else:
            print(report, end="")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
