#!/usr/bin/env python3
"""Read one key from the "Coverage Pipeline" section of a project context file.

    python3 bin/lib/pipeline_config.py --context <target>/ai-workflow/project-context.md --key labels.ready

Exit 0 prints the value; exit 2 when the context file is missing; exit 3 when
the key is missing or empty.
"""
import argparse
import sys
from pathlib import Path

SECTION = "## Coverage Pipeline"


def read_pipeline_config(text):
    values = {}
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == SECTION
            continue
        if inside and line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            values[key.strip()] = value.strip()
    return values


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read one Coverage Pipeline key from a project context file.")
    parser.add_argument("--context", required=True, type=Path, help="path to project-context.md")
    parser.add_argument("--key", required=True, help="key such as labels.ready")
    args = parser.parse_args(argv)
    if not args.context.is_file():
        print(f"pipeline_config: context not found: {args.context}", file=sys.stderr)
        return 2
    value = read_pipeline_config(args.context.read_text(encoding="utf-8")).get(args.key, "")
    if not value:
        print(f"pipeline_config: missing context key: {args.key}", file=sys.stderr)
        return 3
    print(value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
