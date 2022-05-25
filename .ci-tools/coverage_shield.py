import json
import os
import subprocess


def main():
    # assumes coverage.py has already run so the coverage db file already exists

    report_process = subprocess.run(
        ["coverage", "report", "--no-skip-covered", "--rcfile=.coveragerc.ini"],
        capture_output=True,
    )

    with open(".repo-reports/coverage.txt", "wb") as f:
        f.write(report_process.stdout)

    subprocess.run(
        [
            "coverage",
            "json",
            "-o",
            ".repo-reports/coverage.json",
            "--pretty-print",
            "--rcfile=.coveragerc.ini",
        ]
    )

    with open(".repo-reports/coverage.json", "r", encoding="utf-8") as f:
        coverage_result = json.loads(f.read())

    os.unlink(".repo-reports/coverage.json")

    percent_covered = round(coverage_result["totals"]["percent_covered"])

    covered_color = "red"
    if percent_covered > 90:
        covered_color = "yellow"
    if percent_covered > 95:
        covered_color = "#34D058"

    shield_path = ".repo-shields/covered_shield.json"
    with open(shield_path, "w+", encoding="utf-8", newline="\n") as f:
        f.write(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "label": "test coverage",
                    "message": f"{percent_covered}%",
                    "color": covered_color,
                },
            )
        )

    return percent_covered


if __name__ == "__main__":
    main()
