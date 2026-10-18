# OSS Maintainer Audit

[![CI](https://github.com/ian0609666/20261018/actions/workflows/ci.yml/badge.svg)](https://github.com/ian0609666/20261018/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

OSS Maintainer Audit is a small, dependency-free Python CLI that checks whether
an open-source repository contains the basic files and automation needed for
sustainable maintenance.

It produces a score from 0 to 100 and explains which maintenance practices are
already present and which ones should be added next.

## Features

- Audits documentation, governance, security, tests, and automation
- Produces readable terminal output or machine-readable JSON
- Supports CI quality gates through `--fail-under`
- Uses only the Python standard library at runtime
- Works on Windows, macOS, and Linux

## Quick start

Python 3.10 or newer is required.

```bash
python -m pip install -e .
oss-maintainer-audit audit .
```

Run an audit with JSON output:

```bash
oss-maintainer-audit audit /path/to/repository --json
```

Fail when the score is below a chosen threshold:

```bash
oss-maintainer-audit audit . --fail-under 80
```

You can also run the package without installing it:

```bash
PYTHONPATH=src python -m oss_maintainer_audit audit .
```

PowerShell equivalent:

```powershell
$env:PYTHONPATH = "src"
python -m oss_maintainer_audit audit .
```

## What is checked

| Area | Examples | Weight |
| --- | --- | ---: |
| Project overview | `README.md` | 15 |
| License | `LICENSE` or `COPYING` | 15 |
| Contribution guide | `CONTRIBUTING.md` | 10 |
| Community conduct | `CODE_OF_CONDUCT.md` | 10 |
| Security policy | `SECURITY.md` | 10 |
| Release history | `CHANGELOG.md` | 10 |
| Continuous integration | `.github/workflows/*.yml` | 10 |
| Automated tests | `tests/` or common test file patterns | 10 |
| Issue templates | `.github/ISSUE_TEMPLATE/` | 5 |
| Pull request template | `.github/pull_request_template.md` | 5 |

The score is a practical checklist, not a judgment of a project's code quality
or importance to the ecosystem.

## 中文說明

這是一個零執行期相依套件的 Python 命令列工具，用來檢查開源程式碼庫是否具備基本的維護文件、測試、CI、安全政策及協作範本。工具會產生 0–100 分的報告，並列出下一步應補上的項目。

快速執行：

```powershell
$env:PYTHONPATH = "src"
python -m oss_maintainer_audit audit .
```

## Development

```bash
python -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow and
[SECURITY.md](SECURITY.md) for responsible vulnerability reporting.

## License

Released under the [MIT License](LICENSE).
