# Contributing

Thank you for helping improve OSS Maintainer Audit.

## Before opening a change

1. Search existing issues and pull requests.
2. Open an issue for significant behavior or scoring changes.
3. Keep changes focused and avoid unrelated formatting edits.

## Local development

```bash
git clone https://github.com/ian0609666/20261018.git
cd 20261018
python -m unittest discover -s tests -v
```

To run the CLI from the source tree:

```bash
PYTHONPATH=src python -m oss_maintainer_audit audit .
```

## Pull request checklist

- Add or update tests for behavior changes.
- Update the README when the user interface changes.
- Update the changelog for user-visible changes.
- Confirm that all tests pass locally.
- Explain the problem, solution, and any tradeoffs in the pull request.

By participating, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
