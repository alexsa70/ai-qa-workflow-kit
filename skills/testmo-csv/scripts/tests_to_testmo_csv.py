#!/usr/bin/env python3
"""Extract a Testmo-import CSV from pytest + allure test files.

Reference implementation for the kit `testmo-csv` skill. It fills the
*mechanical* fields deterministically (Folder, Name, Steps, Tags, Automated,
State) and best-effort drafts the judgment fields (Description, Pre-conditions,
Expected), marking them `TODO: confirm` when it cannot derive them. The agent
then refines the judgment fields per SKILL.md before the CSV is final.

Header (proven Testmo-import column set):
    Name,Automated,Description,Expected,Folder,Pre-conditions,State,Steps,Tags

Usage:
    python tests_to_testmo_csv.py <file-or-dir> [more ...] -o out.csv
    python tests_to_testmo_csv.py tests/agents_service -o testmo.csv
"""

from __future__ import annotations

import argparse
import ast
import csv
import sys
from pathlib import Path

HEADER = [
    "Name", "Automated", "Description", "Expected",
    "Folder", "Pre-conditions", "State", "Steps", "Tags",
]

HTTPSTATUS_CODES = {
    "OK": 200, "CREATED": 201, "ACCEPTED": 202, "NO_CONTENT": 204,
    "BAD_REQUEST": 400, "UNAUTHORIZED": 401, "FORBIDDEN": 403,
    "NOT_FOUND": 404, "CONFLICT": 409, "UNPROCESSABLE_ENTITY": 422,
    "INTERNAL_SERVER_ERROR": 500,
}


def folder_from_filename(path: Path) -> str:
    stem = path.stem
    if stem.startswith("test_"):
        stem = stem[len("test_"):]
    return " ".join(w.capitalize() for w in stem.split("_") if w)


def humanize(name: str) -> str:
    if name.startswith("test_"):
        name = name[len("test_"):]
    return " ".join(w.capitalize() for w in name.split("_") if w)


def _str_arg(call: ast.Call) -> str | None:
    if call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
        return call.args[0].value
    return None


def _attr_chain(node: ast.AST) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def decorator_info(func: ast.FunctionDef | ast.AsyncFunctionDef):
    """Return (allure_title, marker_set)."""
    title = None
    markers: set[str] = set()
    for dec in func.decorator_list:
        if isinstance(dec, ast.Call):
            chain = _attr_chain(dec.func)
            if chain.endswith("allure.title") or chain.endswith(".title"):
                title = _str_arg(dec) or title
            if ".mark." in chain or chain.startswith("mark."):
                markers.add(chain.split(".")[-1])
        elif isinstance(dec, ast.Attribute):
            chain = _attr_chain(dec)
            if ".mark." in chain:
                markers.add(chain.split(".")[-1])
    return title, markers


def collect_steps(func) -> list[str]:
    steps: list[tuple[int, str]] = []
    for node in ast.walk(func):
        if isinstance(node, ast.With):
            for item in node.items:
                ce = item.context_expr
                if isinstance(ce, ast.Call):
                    chain = _attr_chain(ce.func)
                    if chain.endswith("allure.step") or chain.endswith(".step"):
                        s = _str_arg(ce)
                        if s:
                            steps.append((node.lineno, s))
    steps.sort(key=lambda t: t[0])
    return [s for _, s in steps]


def collect_statuses(func) -> set[int]:
    codes: set[int] = set()
    for node in ast.walk(func):
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            if 100 <= node.value <= 599:
                codes.add(node.value)
        if isinstance(node, ast.Attribute) and node.attr in HTTPSTATUS_CODES:
            codes.add(HTTPSTATUS_CODES[node.attr])
        if isinstance(node, ast.Attribute) and node.attr == "value" and isinstance(node.value, ast.Attribute):
            if node.value.attr in HTTPSTATUS_CODES:
                codes.add(HTTPSTATUS_CODES[node.value.attr])
    return codes


def polarity(markers: set[str], statuses: set[int]) -> str:
    if "negative" in markers:
        return "negative"
    if "positive" in markers:
        return "positive"
    if any(c >= 400 for c in statuses):
        return "negative"
    return "positive"


def fixtures(func) -> list[str]:
    args = [a.arg for a in func.args.args if a.arg != "self"]
    return args


def docstring_summary(func) -> str | None:
    doc = ast.get_docstring(func)
    if not doc:
        return None
    return " ".join(doc.strip().split())


def extract_file(path: Path) -> list[dict]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    folder = folder_from_filename(path)
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            title, markers = decorator_info(node)
            steps = collect_steps(node)
            statuses = collect_statuses(node)
            pol = polarity(markers, statuses)
            name = title or humanize(node.name)
            steps_cell = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps)) or "TODO: confirm"
            desc = docstring_summary(node) or "TODO: confirm"
            fx = fixtures(node)
            precond = "TODO: confirm" + (f" (fixtures: {', '.join(fx)})" if fx else "")
            expected_bits = [s for s in steps if any(k in s.lower() for k in ("assert", "expect", "return", "status"))]
            if statuses:
                expected_bits.append("Status code(s): " + ", ".join(str(c) for c in sorted(statuses)))
            expected = "\n".join(expected_bits) if expected_bits else "TODO: confirm"
            rows.append({
                "Name": name,
                "Automated": "Yes",
                "Description": desc,
                "Expected": expected,
                "Folder": folder,
                "Pre-conditions": precond,
                "State": "Active",
                "Steps": steps_cell,
                "Tags": f"api-automation,{pol}",
            })
    return rows


def iter_files(paths: list[str]):
    for p in paths:
        pp = Path(p)
        if pp.is_dir():
            yield from sorted(pp.rglob("test_*.py"))
        elif pp.is_file():
            yield pp
        else:
            print(f"warning: not found: {p}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="Extract Testmo-import CSV from pytest+allure tests.")
    ap.add_argument("paths", nargs="+", help="test files or directories")
    ap.add_argument("-o", "--out", default="testmo-import.csv", help="output CSV path")
    args = ap.parse_args()

    all_rows = []
    for f in iter_files(args.paths):
        try:
            all_rows.extend(extract_file(f))
        except SyntaxError as e:
            print(f"warning: skip {f}: {e}", file=sys.stderr)

    out = Path(args.out)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(all_rows)

    todo = sum(1 for r in all_rows if "TODO: confirm" in (r["Description"] + r["Expected"] + r["Pre-conditions"]))
    print(f"wrote {len(all_rows)} rows -> {out}", file=sys.stderr)
    print(f"rows needing refinement (TODO): {todo}", file=sys.stderr)
    folders = sorted({r["Folder"] for r in all_rows})
    print(f"folders: {', '.join(folders)}", file=sys.stderr)


if __name__ == "__main__":
    main()
