"""Repository maintenance audit logic."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Rule:
    """A weighted repository maintenance check."""

    key: str
    label: str
    weight: int
    paths: tuple[str, ...] = ()
    globs: tuple[str, ...] = ()
    recommendation: str = ""


@dataclass(frozen=True)
class CheckResult:
    """The result of evaluating one audit rule."""

    key: str
    label: str
    weight: int
    passed: bool
    matches: tuple[str, ...]
    recommendation: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AuditReport:
    """A complete audit of one repository."""

    root: str
    score: int
    maximum_score: int
    rating: str
    checks: tuple[CheckResult, ...]

    @property
    def missing(self) -> tuple[CheckResult, ...]:
        return tuple(check for check in self.checks if not check.passed)

    def to_dict(self) -> dict[str, object]:
        return {
            "root": self.root,
            "score": self.score,
            "maximum_score": self.maximum_score,
            "rating": self.rating,
            "checks": [check.to_dict() for check in self.checks],
        }


RULES: tuple[Rule, ...] = (
    Rule(
        "readme",
        "Project overview",
        15,
        paths=("README.md", "README.rst", "README.txt", "README"),
        recommendation="Add a README with purpose, setup, usage, and support information.",
    ),
    Rule(
        "license",
        "Open-source license",
        15,
        paths=("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"),
        recommendation="Add an OSI-approved license and state it in the README.",
    ),
    Rule(
        "contributing",
        "Contribution guide",
        10,
        paths=("CONTRIBUTING.md", ".github/CONTRIBUTING.md"),
        recommendation="Document setup, tests, review expectations, and the PR workflow.",
    ),
    Rule(
        "code_of_conduct",
        "Code of conduct",
        10,
        paths=("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"),
        recommendation="Publish community behavior and enforcement expectations.",
    ),
    Rule(
        "security",
        "Security policy",
        10,
        paths=("SECURITY.md", ".github/SECURITY.md"),
        recommendation="Explain supported versions and private vulnerability reporting.",
    ),
    Rule(
        "changelog",
        "Release history",
        10,
        paths=("CHANGELOG.md", "HISTORY.md", "NEWS.md"),
        recommendation="Maintain a changelog for notable user-facing changes.",
    ),
    Rule(
        "ci",
        "Continuous integration",
        10,
        globs=(".github/workflows/*.yml", ".github/workflows/*.yaml"),
        recommendation="Run automated tests for proposed changes and supported runtimes.",
    ),
    Rule(
        "tests",
        "Automated tests",
        10,
        paths=("tests", "test"),
        globs=("**/test_*.py", "**/*_test.py", "**/*.test.js", "**/*.spec.ts"),
        recommendation="Add automated tests for core behavior and regressions.",
    ),
    Rule(
        "issue_templates",
        "Issue templates",
        5,
        paths=(".github/ISSUE_TEMPLATE",),
        recommendation="Add structured bug and feature request templates.",
    ),
    Rule(
        "pull_request_template",
        "Pull request template",
        5,
        paths=(
            ".github/pull_request_template.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            "PULL_REQUEST_TEMPLATE.md",
        ),
        recommendation="Prompt contributors to describe changes, tests, and risks.",
    ),
)


def _relative_matches(root: Path, rule: Rule) -> tuple[str, ...]:
    # Case-fold keys so the same file is not reported twice on a
    # case-insensitive file system when a rule accepts multiple casings.
    matches: dict[str, str] = {}

    def add_match(path: Path) -> None:
        relative = path.relative_to(root).as_posix()
        matches.setdefault(relative.casefold(), relative)

    for candidate in rule.paths:
        path = root / candidate
        if path.exists():
            add_match(path)

    for pattern in rule.globs:
        for path in root.glob(pattern):
            if _should_include(path, root):
                add_match(path)

    return tuple(sorted(matches.values(), key=str.casefold))


def _should_include(path: Path, root: Path) -> bool:
    ignored_parts = {".git", ".venv", "venv", "node_modules", "__pycache__"}
    relative_parts = path.relative_to(root).parts
    return path.is_file() and not any(part in ignored_parts for part in relative_parts)


def _rating(score: int) -> str:
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "healthy"
    if score >= 50:
        return "developing"
    return "needs-work"


def audit_repository(root: str | Path, rules: Iterable[Rule] = RULES) -> AuditReport:
    """Audit *root* and return a weighted maintenance report.

    Args:
        root: Directory containing the repository to audit.
        rules: Rules to evaluate. Supplying custom rules is primarily useful for
            embedding this package in another tool.

    Raises:
        FileNotFoundError: If the requested path does not exist.
        NotADirectoryError: If the requested path is not a directory.
    """

    # ``absolute`` avoids surprising failures on virtualized Windows file
    # systems where resolving a sandbox junction can duplicate path segments.
    repository = Path(root).expanduser().absolute()
    if not repository.exists():
        raise FileNotFoundError(f"Repository does not exist: {repository}")
    if not repository.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {repository}")

    results: list[CheckResult] = []
    for rule in rules:
        matches = _relative_matches(repository, rule)
        results.append(
            CheckResult(
                key=rule.key,
                label=rule.label,
                weight=rule.weight,
                passed=bool(matches),
                matches=matches,
                recommendation=rule.recommendation,
            )
        )

    maximum_score = sum(result.weight for result in results)
    score = sum(result.weight for result in results if result.passed)
    return AuditReport(
        root=str(repository),
        score=score,
        maximum_score=maximum_score,
        rating=_rating(score),
        checks=tuple(results),
    )
