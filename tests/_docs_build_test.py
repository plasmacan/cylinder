import shutil
import subprocess


def main():
    shutil.rmtree("docs-preview", ignore_errors=True)
    proc = subprocess.run(
        [
            "sphinx-build",
            "-W",
            "--keep-going",
            "-a",
            "-b",
            "html",
            "docs-src",
            "docs-preview",
        ]
    )
    return proc.returncode


def test_docs():
    assert main() == 0


if __name__ == "__main__":
    main()
