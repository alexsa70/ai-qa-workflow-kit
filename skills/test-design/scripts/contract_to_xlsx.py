#!/usr/bin/env python3
"""Render a Test Design Contract (.md, kit template) into a readable .xlsx.

The .md contract is the source of truth; this writes a derived, read-friendly
spreadsheet next to it (same base name, .xlsx). One row per case on a
`Test Cases` sheet, plus a `Contract` metadata sheet.

Usage:
    python contract_to_xlsx.py path/to/contract.md [-o path/to/out.xlsx]

Requires openpyxl:  pip install openpyxl --break-system-packages
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    from openpyxl.utils import get_column_letter
except ImportError:
    sys.exit("openpyxl is required: pip install openpyxl --break-system-packages")

CASE_COLUMNS = [
    "ID", "Name", "Priority", "Request actor", "Target variants",
    "Preconditions", "Steps", "Expected", "API status",
    "Business assertions", "Side effects", "Cleanup", "Evidence",
]

# Map contract bullet labels -> case dict keys.
TOP_LABELS = {
    "priority": "Priority",
    "request actor": "Request actor",
    "target variants": "Target variants",
    "given": "Preconditions",
    "when": "Steps",
    "then": "Expected",
    "cleanup": "Cleanup",
    "evidence": "Evidence",
}
API_LABELS = {
    "status": "API status",
    "business assertions": "Business assertions",
    "side effects": "Side effects",
}
META_LABELS = ["Project", "Status", "Requirement source", "Scope",
               "Exclusions", "Next transition"]


def parse_contract(text: str):
    meta = {}
    for label in META_LABELS:
        m = re.search(rf"^- {re.escape(label)}:\s*(.*)$", text, re.MULTILINE | re.IGNORECASE)
        if m:
            meta[label] = m.group(1).strip().strip("`")

    cases = []
    # Split on case headers: ### TC-001: name
    parts = re.split(r"^###\s+(TC-[^\s:]+):?\s*(.*)$", text, flags=re.MULTILINE)
    # parts: [pre, id1, name1, body1, id2, name2, body2, ...]
    for i in range(1, len(parts), 3):
        cid = parts[i].strip()
        name = parts[i + 1].strip()
        body = parts[i + 2]
        case = {c: "" for c in CASE_COLUMNS}
        case["ID"] = cid
        case["Name"] = name
        _parse_case_body(body, case)
        cases.append(case)
    return meta, cases


def _parse_case_body(body: str, case: dict):
    lines = body.splitlines()
    cur_key = None
    in_api = False
    buf: list[str] = []

    def flush():
        nonlocal buf, cur_key
        if cur_key and buf:
            val = "\n".join(b.rstrip() for b in buf).strip()
            case[cur_key] = (case[cur_key] + "\n" + val).strip() if case[cur_key] else val
        buf = []

    for raw in lines:
        line = raw.rstrip()
        m_top = re.match(r"^- ([A-Za-z][A-Za-z /]+):\s*(.*)$", line)
        m_api = re.match(r"^\s{2,}- ([A-Za-z][A-Za-z /]+):\s*(.*)$", line)
        if m_top:
            flush()
            label = m_top.group(1).strip().lower()
            rest = m_top.group(2).strip()
            in_api = label.startswith("api response")
            if in_api:
                cur_key = None
                continue
            cur_key = TOP_LABELS.get(label)
            buf = [rest] if rest else []
        elif m_api and in_api:
            flush()
            label = m_api.group(1).strip().lower()
            rest = m_api.group(2).strip()
            cur_key = API_LABELS.get(label)
            buf = [rest] if rest else []
        else:
            # continuation (nested bullets / wrapped text)
            stripped = line.strip()
            if stripped.startswith("- "):
                stripped = stripped[2:]
            if stripped and cur_key:
                buf.append(stripped)
    flush()


def build_workbook(meta: dict, cases: list[dict]) -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "Test Cases"

    header_font = Font(bold=True)
    wrap_top = Alignment(wrap_text=True, vertical="top")

    ws.append(CASE_COLUMNS)
    for c in ws[1]:
        c.font = header_font
        c.alignment = Alignment(vertical="top")
    for case in cases:
        ws.append([case.get(col, "") for col in CASE_COLUMNS])

    widths = {
        "ID": 10, "Name": 40, "Priority": 10, "Request actor": 16,
        "Target variants": 20, "Preconditions": 40, "Steps": 45,
        "Expected": 45, "API status": 12, "Business assertions": 35,
        "Side effects": 25, "Cleanup": 25, "Evidence": 20,
    }
    for idx, col in enumerate(CASE_COLUMNS, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = widths.get(col, 20)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = wrap_top
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(CASE_COLUMNS))}1"

    ws2 = wb.create_sheet("Contract")
    ws2.append(["Field", "Value"])
    for c in ws2[1]:
        c.font = header_font
    for label in META_LABELS:
        ws2.append([label, meta.get(label, "")])
    ws2.column_dimensions["A"].width = 22
    ws2.column_dimensions["B"].width = 70
    for row in ws2.iter_rows(min_row=2):
        row[1].alignment = Alignment(wrap_text=True, vertical="top")
    return wb


def main():
    ap = argparse.ArgumentParser(description="Render a test design contract .md to a readable .xlsx.")
    ap.add_argument("contract", help="path to the contract .md")
    ap.add_argument("-o", "--out", help="output .xlsx (default: contract path with .xlsx)")
    args = ap.parse_args()

    src = Path(args.contract)
    if not src.is_file():
        sys.exit(f"contract not found: {src}")
    out = Path(args.out) if args.out else src.with_suffix(".xlsx")

    meta, cases = parse_contract(src.read_text(encoding="utf-8"))
    if not cases:
        print("warning: no TC-* cases found; writing metadata-only workbook", file=sys.stderr)
    wb = build_workbook(meta, cases)
    wb.save(out)
    print(f"wrote {len(cases)} cases -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
