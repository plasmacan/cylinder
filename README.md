# Plasma Cylinder

[![code testing](https://github.com/plasmacan/cylinder/actions/workflows/testing.yaml/badge.svg)](https://github.com/plasmacan/cylinder/actions/workflows/testing.yaml)
[![CodeQL](https://github.com/plasmacan/cylinder/actions/workflows/codeql.yaml/badge.svg)](https://github.com/plasmacan/cylinder/actions/workflows/codeql.yaml)
[![code coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/plasmacan/cylinder/main/.repo-shields/covered_shield.json)](.repo-reports/coverage.txt)
[![code quality](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/plasmacan/cylinder/main/.repo-shields/quality_shield.json)](.repo-reports/ruff-report.txt)
[![PyPI version](https://badge.fury.io/py/cylinder.svg)](https://badge.fury.io/py/cylinder)

Cylinder is a small, opinionated WSGI web framework built on top of
[werkzeug](https://werkzeug.palletsprojects.com).

It is designed for developers who want web applications to stay simple, readable, and predictable. By
keeping routing visible in the filesystem and avoiding unnecessary abstractions, Cylinder makes
applications easier to reason about and easier to troubleshoot.

Key features include:

-   File-based routing that reflects the URL structure on disk
-   Minimal configuration and explicit application wiring
-   Support for hooks, custom error handlers, and method-based routing via filenames

Cylinder aims to provide just enough structure to guide development without hiding how the application
works.

For additional information please review the full documentation at
[plasmacan.github.io/cylinder](https://plasmacan.github.io/cylinder/)
