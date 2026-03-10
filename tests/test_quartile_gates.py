#!/usr/bin/env python3
"""
tests/test_quartile_gates.py — AutoResearch Room 5 Evaluator
=============================================================
Tests that validate_submission.py correctly enforces quartile-specific
quality gates across six fixture papers.

Scoring:
  composite_score = 0.6 * base_accuracy + 0.4 * quartile_bonus

Usage:
  python3 tests/test_quartile_gates.py           # human-readable report
  python3 tests/test_quartile_gates.py --score    # JSON output
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from validate_submission import validate_draft  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"

# (filename, expected_has_errors, label)
CASES = [
    ("good_conference_paper.md", False, "good_conference"),
    ("good_q3_paper.md",         False, "good_q3"),
    ("bad_ai_prose.md",          True,  "bad_ai_prose"),
    ("bad_no_data.md",           True,  "bad_no_data"),
    ("bad_q1_missing_field_data.md", True,  "bad_q1"),
    ("bad_q2_no_novelty.md",     True,  "bad_q2"),
]


def run_validate(path: Path) -> list[dict]:
    """Run validate_draft with crash protection. Returns issues or a
    synthetic ERROR entry if the validator crashes."""
    try:
        return validate_draft(path)
    except Exception as exc:
        return [{"severity": "ERROR", "check": "crash",
                 "msg": f"validate_draft crashed: {exc}"}]


def has_errors(issues: list[dict]) -> bool:
    return any(i["severity"] == "ERROR" for i in issues)


def check_quartile_signals(results: dict[str, list[dict]]) -> dict:
    """Evaluate quartile-specific signals beyond simple pass/fail."""
    checks = {}

    # Q1: should flag insufficient refs (need 40+)
    q1 = results.get("bad_q1", [])
    q1_msgs = " ".join(i["msg"] for i in q1)
    checks["q1_refs_flagged"] = any(
        "reference" in i["msg"].lower() and i["check"] == "journal_spec"
        for i in q1
    )

    # Q1: should flag missing required sections (Literature Review, Data Availability, Discussion)
    checks["q1_sections_flagged"] = any(
        "missing" in i["msg"].lower() and "section" in i["msg"].lower()
        for i in q1
    )

    # Q2: should flag insufficient refs (need 30+)
    q2 = results.get("bad_q2", [])
    checks["q2_refs_flagged"] = any(
        "reference" in i["msg"].lower() and i["check"] == "journal_spec"
        for i in q2
    )

    # Q3 good paper: should pass (0 errors)
    q3 = results.get("good_q3", [])
    checks["q3_passed"] = not has_errors(q3)

    return checks


def evaluate() -> dict:
    """Run all fixtures and compute composite score."""
    tp, tn, fp, fn = 0, 0, 0, 0
    all_results: dict[str, list[dict]] = {}

    for filename, expect_errors, label in CASES:
        path = FIXTURES / filename
        if not path.exists():
            # Missing fixture counts as wrong prediction
            if expect_errors:
                fn += 1
            else:
                fp += 1
            all_results[label] = []
            continue

        issues = run_validate(path)
        all_results[label] = issues
        got_errors = has_errors(issues)

        if expect_errors and got_errors:
            tp += 1
        elif expect_errors and not got_errors:
            fn += 1
        elif not expect_errors and not got_errors:
            tn += 1
        else:
            fp += 1

    total = tp + tn + fp + fn
    base_accuracy = (tp + tn) / total if total else 0.0

    q_checks = check_quartile_signals(all_results)
    q_total = len(q_checks)
    q_hits = sum(1 for v in q_checks.values() if v)
    quartile_bonus = q_hits / q_total if q_total else 0.0

    composite = 0.6 * base_accuracy + 0.4 * quartile_bonus

    return {
        "composite_score": round(composite, 4),
        "details": {
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "total_fixtures": total,
            "quartile_checks": q_checks,
            "quartile_bonus": round(quartile_bonus, 4),
        },
    }


def print_report(result: dict, all_issues: dict[str, list[dict]]) -> None:
    """Print human-readable report."""
    d = result["details"]
    print("=" * 60)
    print("  QUARTILE GATES EVALUATOR — Room 5")
    print("=" * 60)
    print()

    for filename, expect_errors, label in CASES:
        path = FIXTURES / filename
        issues = all_issues.get(label, [])
        got_errors = has_errors(issues)
        errors = [i for i in issues if i["severity"] == "ERROR"]
        status = "PASS" if (expect_errors == got_errors) else "FAIL"
        icon = "[OK]" if status == "PASS" else "[X]"
        print(f"  {icon} {filename}")
        print(f"      expected_errors={expect_errors}  got_errors={got_errors}  "
              f"error_count={len(errors)}")
        if errors:
            for e in errors[:5]:
                print(f"        - [{e['check']}] {e['msg']}")
            if len(errors) > 5:
                print(f"        ... and {len(errors) - 5} more")
        print()

    print("-" * 60)
    print(f"  TP={d['true_positives']}  TN={d['true_negatives']}  "
          f"FP={d['false_positives']}  FN={d['false_negatives']}  "
          f"total={d['total_fixtures']}")
    print()
    print("  Quartile-specific checks:")
    for k, v in d["quartile_checks"].items():
        print(f"    {k}: {'FIRED' if v else 'missed'}")
    print()
    print(f"  base_accuracy:   {(d['true_positives'] + d['true_negatives']) / d['total_fixtures']:.2%}")
    print(f"  quartile_bonus:  {d['quartile_bonus']:.2%}")
    print(f"  composite_score: {result['composite_score']:.4f}")
    print("=" * 60)


def main() -> None:
    score_mode = "--score" in sys.argv

    # Collect issues for report
    all_issues: dict[str, list[dict]] = {}
    for filename, _, label in CASES:
        path = FIXTURES / filename
        if path.exists():
            all_issues[label] = run_validate(path)
        else:
            all_issues[label] = []

    result = evaluate()

    if score_mode:
        print(json.dumps(result, indent=2))
    else:
        print_report(result, all_issues)

    # Exit code: 0 if composite >= 0.5, else 1
    sys.exit(0 if result["composite_score"] >= 0.5 else 1)


if __name__ == "__main__":
    main()
