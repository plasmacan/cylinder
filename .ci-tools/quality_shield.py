import io
import json

from pylint.lint import Run
from pylint.reporters.text import TextReporter


def main():

    with io.StringIO() as f:
        results = Run(
            [".", "--recursive=y", "--rcfile", ".pylintrc.ini"],
            reporter=TextReporter(f),
            exit=False,
        )
        report = f.getvalue()

    average_score = round(results.linter.stats.global_note, 1)
    problems_path = ".repo-reports/pylint-report.txt"
    with open(problems_path, "w+", encoding="utf-8", newline="\n") as f:
        f.write("output from recursive pylint:\n")
        f.write(report)

    score_color = "red"
    if average_score > 9:
        score_color = "yellow"
    if average_score > 9.5:
        score_color = "#34D058"

    shield_path = ".repo-shields/quality_shield.json"
    with open(shield_path, "w+", encoding="utf-8", newline="\n") as f:
        f.write(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "label": "code quality",
                    "message": f"{average_score}/10",
                    "color": score_color,
                },
            )
        )

    return average_score


if __name__ == "__main__":
    main()
