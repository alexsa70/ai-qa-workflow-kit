#!/usr/bin/env python3
"""Choose which open pull requests the night shift may take.

A pull request is eligible when it is an open draft with the ready label, the
last `labeled` event for that label (not undone by an `unlabeled` event) came
from neither a bot nor the night-shift account, it has neither the done nor the
blocked label, no comment carrying "night-shift run " is newer than that event,
and it changes no file that another open pull request also changes.

The selector fails closed: missing, malformed or ambiguous data skips the pull
request, it never makes it eligible.

Prints "<number>\\t<branch>" per eligible pull request, after all are processed;
reasons for skips go to stderr as "skip #<number>: <reason>".
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPORT_MARKER = "night-shift run "


class Skip(Exception):
    """A pull request is skipped for a stated reason."""


def load_json_items(path):
    path = Path(path)
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return data if isinstance(data, list) else [data]


def label_names(pr):
    return {label["name"] for label in pr.get("labels", [])}


def changed_files(pr):
    return {item["path"] for item in pr.get("files", [])}


def has_timestamp(item):
    return isinstance(item.get("created_at"), str) and bool(item["created_at"])


def last_label_event(events, label):
    latest = None
    for event in sorted(events, key=lambda item: item.get("created_at") or ""):
        if (event.get("label") or {}).get("name") != label:
            continue
        if event.get("event") == "labeled":
            latest = event
        elif event.get("event") == "unlabeled":
            latest = None
    return latest


def is_human(actor, bot_pattern, night_actor):
    if not actor:
        return False
    login = actor.get("login")
    if not isinstance(login, str) or not login:
        return False
    if actor.get("type") == "Bot" or re.search(bot_pattern, login):
        return False
    return not (night_actor and login.lower() == night_actor.lower())


def classify(pr, events, comments, others, labels, bot_pattern, night_actor):
    names = label_names(pr)
    if not pr.get("isDraft"):
        return "skipped", "not a draft"
    if labels["ready"] not in names:
        return "skipped", "no ready label"
    for key in ("done", "blocked"):
        if labels[key] in names:
            return "skipped", f"has the {labels[key]} label"
    for item in events:
        if (item.get("label") or {}).get("name") == labels["ready"] and not has_timestamp(item):
            return "skipped", "ready label event without timestamp"
    event = last_label_event(events, labels["ready"])
    if event is None:
        return "skipped", "no labeled event for the ready label"
    actor = event.get("actor") or {}
    if not is_human(actor, bot_pattern, night_actor):
        return "skipped", f"ready label applied by {actor.get('login', 'unknown')}"
    labelled_at = event["created_at"]
    for comment in comments:
        if REPORT_MARKER not in (comment.get("body") or ""):
            continue
        if not has_timestamp(comment):
            return "skipped", "a night-shift report without timestamp"
        if comment["created_at"] >= labelled_at:
            return "skipped", "a night-shift report is not older than the ready label"
    shared = set()
    for other in others:
        shared |= changed_files(pr) & changed_files(other)
    if shared:
        return "skipped", "files also changed by another open PR: " + ", ".join(sorted(shared))
    return "eligible", ""


def main(argv=None):
    parser = argparse.ArgumentParser(description="Choose the pull requests the night shift may take.")
    parser.add_argument("--prs", required=True, type=Path, help="gh pr list JSON (all open PRs)")
    parser.add_argument("--events-dir", required=True, type=Path, help="dir with <n>.events.json and <n>.comments.json")
    parser.add_argument("--label-ready", required=True)
    parser.add_argument("--label-done", required=True)
    parser.add_argument("--label-blocked", required=True)
    parser.add_argument("--night-actor", default="", help="login the night shift acts as, if distinct")
    parser.add_argument("--bot-pattern", default=r"\[bot\]$")
    parser.add_argument("--only", type=int, help="consider only this pull request number")
    args = parser.parse_args(argv)

    labels = {"ready": args.label_ready, "done": args.label_done, "blocked": args.label_blocked}
    if not args.prs.is_file():
        print(f"select_ready_prs: cannot read PR list: {args.prs}", file=sys.stderr)
        return 2
    try:
        prs = load_json_items(args.prs)
    except (OSError, ValueError):
        print(f"select_ready_prs: cannot read PR list: {args.prs}", file=sys.stderr)
        return 2

    eligible = []
    for item in prs:
        number = "?"
        try:
            number = item["number"]
            if labels["ready"] not in label_names(item):
                continue
            if args.only is not None and number != args.only:
                continue
            events_path = args.events_dir / f"{number}.events.json"
            comments_path = args.events_dir / f"{number}.comments.json"
            if not events_path.is_file():
                raise Skip("events not fetched")
            if not comments_path.is_file():
                raise Skip("comments not fetched")
            others = [other for other in prs if other.get("number") != number]
            status, reason = classify(item, load_json_items(events_path), load_json_items(comments_path),
                                      others, labels, args.bot_pattern, args.night_actor)
            if status == "eligible":
                eligible.append(f"{number}\t{item['headRefName']}")
            else:
                print(f"skip #{number}: {reason}", file=sys.stderr)
        except Skip as skip:
            print(f"skip #{number}: {skip}", file=sys.stderr)
        except Exception as error:  # fail closed: one bad record must not abort or admit
            print(f"skip #{number}: unreadable data ({type(error).__name__})", file=sys.stderr)
    for line in eligible:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
