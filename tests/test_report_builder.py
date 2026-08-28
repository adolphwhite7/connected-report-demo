import json
import tempfile
import unittest
from pathlib import Path

from report_builder import Finding, build_report, load_findings, select_findings


def finding(finding_id: str, theme: str = "Intake quality") -> Finding:
    return Finding(
        finding_id=finding_id,
        title=f"Title {finding_id}",
        theme=theme,
        summary=f"Summary for {finding_id}.",
        evidence=(f"Evidence for {finding_id}.",),
        recommended_action=f"Act on {finding_id}.",
        source_label="Example source",
        source_url="https://example.com/",
    )


class ReportBuilderTests(unittest.TestCase):
    def test_selection_preserves_requested_order(self) -> None:
        available = [finding("F-101"), finding("F-102")]
        selected = select_findings(available, ["F-102", "F-101"])
        self.assertEqual([item.finding_id for item in selected], ["F-102", "F-101"])

    def test_report_connects_findings_that_share_a_theme(self) -> None:
        report = build_report("Review", [finding("F-101"), finding("F-103")])
        self.assertIn("F-101 and F-103 identify related parts", report)
        self.assertIn("Included finding IDs: F-101, F-103", report)

    def test_unknown_selection_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown finding IDs: F-999"):
            select_findings([finding("F-101")], ["F-999"])

    def test_duplicate_selections_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Select each finding ID once: F-101"):
            select_findings([finding("F-101")], ["F-101", "F-101"])

    def test_markdown_source_url_is_encoded(self) -> None:
        item = finding("F-101")
        item = Finding(
            **{
                **item.__dict__,
                "source_label": "Example [source]",
                "source_url": "https://example.com/report_(final)",
            }
        )
        report = build_report("Review", [item])
        self.assertIn(
            "[Example \\[source\\]](https://example.com/report_%28final%29)", report
        )

    def test_duplicate_ids_are_rejected(self) -> None:
        payload = {
            "findings": [
                self._record("F-101", "https://example.com/"),
                self._record("F-101", "https://example.com/"),
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "findings.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate finding IDs: F-101"):
                load_findings(path)

    def test_non_web_source_url_is_rejected(self) -> None:
        payload = {"findings": [self._record("F-101", "file:///private/source")]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "findings.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Source URL must use http or https"):
                load_findings(path)

    @staticmethod
    def _record(finding_id: str, source_url: str) -> dict[str, object]:
        return {
            "id": finding_id,
            "title": "Example finding",
            "theme": "Intake quality",
            "summary": "An example summary.",
            "evidence": ["An example observation."],
            "recommended_action": "Take an example action.",
            "source": {"label": "Example source", "url": source_url},
        }


if __name__ == "__main__":
    unittest.main()
