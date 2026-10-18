from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from oss_maintainer_audit.audit import audit_repository
from oss_maintainer_audit.cli import main, render_text


class AuditRepositoryTests(unittest.TestCase):
    def test_empty_repository_has_zero_score(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = audit_repository(directory)

        self.assertEqual(report.score, 0)
        self.assertEqual(report.maximum_score, 100)
        self.assertEqual(report.rating, "needs-work")
        self.assertEqual(len(report.missing), 10)

    def test_common_files_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Project", encoding="utf-8")
            (root / "LICENSE").write_text("MIT", encoding="utf-8")
            workflow = root / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "ci.yaml").write_text("name: CI", encoding="utf-8")
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_example.py").write_text("", encoding="utf-8")

            report = audit_repository(root)

        self.assertEqual(report.score, 50)
        self.assertEqual(report.rating, "developing")
        passed = {check.key for check in report.checks if check.passed}
        self.assertEqual(passed, {"readme", "license", "ci", "tests"})

    def test_nonexistent_repository_is_rejected(self) -> None:
        with self.assertRaises(FileNotFoundError):
            audit_repository("path-that-does-not-exist")

    def test_text_report_includes_recommendations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = audit_repository(directory)

        output = render_text(report)
        self.assertIn("Maintenance score: 0/100", output)
        self.assertIn("[MISS] Security policy", output)
        self.assertIn("Next:", output)


class CliTests(unittest.TestCase):
    def test_json_output_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["audit", directory, "--json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["score"], 0)
        self.assertEqual(len(payload["checks"]), 10)

    def test_fail_under_returns_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(StringIO()):
                exit_code = main(["audit", directory, "--fail-under", "80"])

        self.assertEqual(exit_code, 1)

    def test_missing_path_returns_two(self) -> None:
        stderr = StringIO()
        with redirect_stderr(stderr):
            exit_code = main(["audit", "path-that-does-not-exist"])

        self.assertEqual(exit_code, 2)
        self.assertIn("does not exist", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
