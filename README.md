# Hello-Wolrd-CI

[![code testing](https://github.com/grintor/Hello-Wolrd-CI/actions/workflows/testing.yaml/badge.svg)](https://github.com/grintor/Hello-World-CI/actions/workflows/testing.yaml)
[![CodeQL](https://github.com/grintor/Hello-Wolrd-CI/actions/workflows/codeql.yaml/badge.svg)](https://github.com/grintor/Hello-Wolrd-CI/actions/workflows/codeql.yaml)
[![code coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/grintor/Hello-Wolrd-CI/main/.repo-shields/covered_shield.json)](.repo-reports/coverage.txt)
[![code quality](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/grintor/Hello-Wolrd-CI/main/.repo-shields/quality_shield.json)](.repo-reports/pylint-report.txt)

A template for GitHub Actions with pylint, pre-commit, and coverage.py and various other tools

1. clone the repo
2. pip -r requirements.txt
3. pre-commit install
4. git checkout staging

To test, just run "pytest" in the repo root and look in results The test coverage reports are located in
.repo-reports/coverage/index.html after the tests are ran. CI will fail if the coverage is not above 90% and if the
code quality is not above 90%
