import json
import subprocess


def main():

    result = subprocess.run(
        ["ruff", "check", ".", "--output-format", "concise"],
        capture_output=True,
        text=True,
    )
    report = result.stdout + result.stderr

    warning_count = sum(
        1 for line in result.stdout.splitlines() if line.strip() and not line.startswith("Found") and ":" in line
    )

    problems_path = ".repo-reports/ruff-report.txt"
    with open(problems_path, "w+", encoding="utf-8", newline="\n") as f:
        f.write("output from ruff check:\n")
        f.write(report)

    if warning_count == 0:
        score_color = "#34D058"
        message = "0 warnings"
    elif warning_count <= 5:
        score_color = "yellow"
        message = f"{warning_count} warnings"
    else:
        score_color = "red"
        message = f"{warning_count} warnings"

    shield_path = ".repo-shields/quality_shield.json"
    with open(shield_path, "w+", encoding="utf-8", newline="\n") as f:
        f.write(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "label": "code quality",
                    "message": message,
                    "color": score_color,
                },
            )
        )

    return warning_count


if __name__ == "__main__":
    main()
