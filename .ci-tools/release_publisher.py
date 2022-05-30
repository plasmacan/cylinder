import os
import re
import shutil
import subprocess
import sys

sys.path.append(os.getcwd())

import src.cylinder  # pylint: disable=wrong-import-position

# flake8: noqa:T001

code_version = src.cylinder.__version__

print(f"code version is {code_version}")

release_version = sys.argv[1]

print(f"release version is {release_version}")

if not code_version.startswith("v"):
    print('code version must start with "v" to publish')
    sys.exit(1)

if not release_version.startswith("v"):
    print('release version must start with "v" to publish')
    sys.exit(2)

if re.search("[a-zA-Z]", release_version.split("v")[1]):
    print("release version must not have alpha suffix")
    sys.exit(3)

if re.search("[a-zA-Z]", code_version.split("v")[1]):
    print("code version must not have alpha suffix")
    sys.exit(4)

if "-" in code_version:
    print("code version must not have a dash")
    sys.exit(5)

if "-" in release_version:
    print("release version must not have a dash")
    sys.exit(6)

if code_version != release_version:
    print("version mismatch")
    sys.exit(7)

shutil.rmtree("dist", ignore_errors=True)
shutil.rmtree("build", ignore_errors=True)

subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"], check=True)
subprocess.run(["twine", "check", "dist/*"], check=True)
subprocess.run(["twine", "check", "dist/*"], check=True)
subprocess.run(
    [
        "twine",
        "upload",
        "--repository-url",
        os.environ["REPO_URL"],
        "dist/*",
        "--non-interactive",
        "--username",
        os.environ["PYPI_USER"],
        "--password",
        os.environ["PYPI_KEY"],
    ],
    check=True,
)
