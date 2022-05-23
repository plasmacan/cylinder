import shutil
import subprocess


def main():
    shutil.rmtree(".repo-reports/docs-preview", ignore_errors=True)
    proc = subprocess.run(
        [
            "sphinx-build",
            "-W",
            "--keep-going",
            "-a",
            "-b",
            "html",
            "docs-src",
            ".repo-reports/docs-preview",
        ]
    )
    return proc.returncode


def test_docs():
    assert main() == 0


if __name__ == "__main__":
    main()
