from __future__ import annotations

import csv
import os
from datetime import datetime

RESULTS_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "results.csv"))


def record_result(
    case_id: str,
    status: str,
    actual_result: str,
    evidence_defect: str = "",
    tester: str = "Antigravity QA Agent",
) -> None:
    """Record test case result into evidence/results.csv."""
    assert status in {"PASS", "FAIL", "BLOCKED", "NOT RUN"}, f"Invalid status {status}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tester_time = f"{tester} / {timestamp}"

    rows = []
    found = False
    with open(RESULTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)
        for row in reader:
            if row and row[0] == case_id:
                rows.append([case_id, status, actual_result, evidence_defect, tester_time])
                found = True
            else:
                rows.append(row)

    if not found:
        rows.append([case_id, status, actual_result, evidence_defect, tester_time])

    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def get_summary_stats() -> dict[str, int | float]:
    """Calculate test execution statistics."""
    counts = {"PASS": 0, "FAIL": 0, "BLOCKED": 0, "NOT RUN": 0}
    total = 0
    with open(RESULTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row:
                st = row[1]
                counts[st] = counts.get(st, 0) + 1
                total += 1

    executed = counts["PASS"] + counts["FAIL"] + counts["BLOCKED"]
    pass_denom = counts["PASS"] + counts["FAIL"]
    pass_rate = round((counts["PASS"] / pass_denom * 100), 2) if pass_denom > 0 else 0.0
    coverage = round((executed / total * 100), 2) if total > 0 else 0.0

    return {
        "total": total,
        "executed": executed,
        "PASS": counts["PASS"],
        "FAIL": counts["FAIL"],
        "BLOCKED": counts["BLOCKED"],
        "NOT_RUN": counts["NOT RUN"],
        "pass_rate": pass_rate,
        "coverage": coverage,
    }
