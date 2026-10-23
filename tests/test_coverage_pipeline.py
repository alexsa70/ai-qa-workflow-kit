import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PIPELINE_KEYS = [
    "coverage.uncovered_command",
    "coverage.detail_command",
    "coverage.day_batch_size",
    "requirements.source",
    "requirements.inventory_paths",
    "backend.checkout",
    "authoring.skill",
    "authoring.after_checkpoint_phases",
    "checks.safe",
    "checks.preflight",
    "run.live_sandbox",
    "review.command",
    "labels.ready",
    "labels.done",
    "labels.blocked",
    "night.permission_mode",
    "night.allowed_tools",
    "night.max_turns",
    "night.timeout_minutes",
    "night.actor_login",
    "heuristics.project_file",
]

PROJECT_TERMS = [
    "kal sense",
    "kal-sense",
    "kaleidoo",
    "it-dgx",
    "catalog/",
    "route_coverage",
    "catalog-test",
    "testmo project 5",
]


def load_module(relative_path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PipelineConfigTests(unittest.TestCase):
    def test_template_declares_every_pipeline_key(self):
        config = load_module("bin/lib/pipeline_config.py", "pipeline_config")
        text = (ROOT / "templates" / "project-context.md").read_text(encoding="utf-8")
        self.assertIn("## Coverage Pipeline", text)
        values = config.read_pipeline_config(text)
        for key in PIPELINE_KEYS:
            self.assertIn(key, values, key)

    def test_reader_ignores_other_sections(self):
        config = load_module("bin/lib/pipeline_config.py", "pipeline_config")
        text = (
            "## Paths\n\n- labels.ready: wrong\n\n"
            "## Coverage Pipeline\n\n- labels.ready: afk-ready\n"
            "- night.allowed_tools: Bash(git push origin HEAD:*),Read\n\n"
            "## Known Constraints\n\n- labels.done: wrong\n"
        )
        values = config.read_pipeline_config(text)
        self.assertEqual(values["labels.ready"], "afk-ready")
        self.assertEqual(values["night.allowed_tools"], "Bash(git push origin HEAD:*),Read")
        self.assertNotIn("labels.done", values)

    def test_cli_reports_missing_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            context = Path(tmp) / "project-context.md"
            context.write_text("## Coverage Pipeline\n\n- labels.ready:\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "bin/lib/pipeline_config.py"),
                 "--context", str(context), "--key", "labels.ready"],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 3)
        self.assertIn("missing context key: labels.ready", result.stderr)

    def test_cli_help(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "bin/lib/pipeline_config.py"), "--help"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout.lower())


class ProjectAgnosticTests(unittest.TestCase):
    def test_kit_skills_agents_and_templates_name_no_project(self):
        for folder in ("skills", "agents", "templates"):
            for path in (ROOT / folder).rglob("*"):
                if not path.is_file() or path.suffix not in {".md", ".yaml", ".json", ".py"}:
                    continue
                text = path.read_text(encoding="utf-8").lower()
                for term in PROJECT_TERMS:
                    self.assertNotIn(term, text, f"{path.relative_to(ROOT)} names '{term}'")


PIPELINE_SKILLS = ["coverage-backlog", "requirement-grill", "blackbox-review", "night-shift"]


class PipelineSkillTests(unittest.TestCase):
    def test_pipeline_skills_exist_and_are_small(self):
        for name in PIPELINE_SKILLS:
            path = ROOT / "skills" / name / "SKILL.md"
            self.assertTrue(path.is_file(), name)
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertLessEqual(len(lines), 200, f"{name}: {len(lines)} lines")

    def test_orchestrator_routes_pipeline_skills(self):
        text = (ROOT / "agents" / "qa-orchestrator.md").read_text(encoding="utf-8")
        self.assertIn("`coverage-planning`", text)
        for name in PIPELINE_SKILLS:
            self.assertIn(f"Use `{name}` when:", text, name)

    def test_launchers_allow_the_project_authoring_skill(self):
        for relative in ("bin/qa-kit", "docs/kit-only-mode.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("authoring.skill", text, relative)

    def test_grill_brief_has_required_sections(self):
        text = (ROOT / "skills/requirement-grill/assets/grill-brief.md").read_text(encoding="utf-8")
        for heading in ("## Units", "## Three questions", "## Cases", "## Not claimed",
                        "## Rejected options", "## Open questions", "## Sources read"):
            self.assertIn(heading, text, heading)


HEURISTIC_FIELDS = ["Applies when", "Try", "User expects", "Typical failure", "Technique", "Source"]
TECHNIQUES = {"boundary", "equivalence", "state", "decision-table", "error-guessing", "journey",
              "concurrency", "interruption", "data", "roles", "recovery"}


def heuristic_entries(text):
    # The format example inside a code fence ("### H-<AREA>-<NN> ...") is not an entry.
    blocks = re.split(r"^### ", text, flags=re.MULTILINE)[1:]
    return [block for block in blocks if re.match(r"H-[A-Z]+-\d{2} ", block)]


class HeuristicsFormatTests(unittest.TestCase):
    def check_file(self, relative, minimum):
        text = (ROOT / relative).read_text(encoding="utf-8")
        entries = heuristic_entries(text)
        self.assertGreaterEqual(len(entries), minimum, relative)
        ids = set()
        for entry in entries:
            entry_id = entry.split(" ", 1)[0]
            self.assertRegex(entry_id, r"^H-[A-Z]+-\d{2}$", entry_id)
            self.assertNotIn(entry_id, ids, entry_id)
            ids.add(entry_id)
            for field in HEURISTIC_FIELDS:
                self.assertIn(f"- **{field}:**", entry, f"{entry_id} lacks {field}")
            technique = re.search(r"- \*\*Technique:\*\* (\S+)", entry).group(1)
            self.assertIn(technique, TECHNIQUES, entry_id)

    def test_kit_heuristics(self):
        self.check_file("skills/blackbox-review/references/heuristics.md", 7)

    def test_project_heuristics_template(self):
        self.check_file("templates/project-heuristics.md", 1)

    def test_findings_template_names_every_category(self):
        text = (ROOT / "skills/blackbox-review/assets/findings.md").read_text(encoding="utf-8")
        for category in ("variant", "new-case-in-inventory", "outside-inventory", "question"):
            self.assertIn(category, text, category)


class NightShiftContentTests(unittest.TestCase):
    def test_prompt_has_every_placeholder(self):
        text = (ROOT / "skills/night-shift/assets/night-prompt.md").read_text(encoding="utf-8")
        for placeholder in ("{{PR}}", "{{BRANCH}}", "{{RUN_ID}}", "{{KIT_DIR}}", "{{TARGET}}"):
            self.assertIn(placeholder, text, placeholder)
        self.assertIn("night-shift run {{RUN_ID}}", text)

    def test_skill_forbids_approval_and_merge(self):
        text = (ROOT / "skills/night-shift/SKILL.md").read_text(encoding="utf-8")
        for phrase in ("gh pr ready", "merge", "approval", "force-push", "bypassPermissions",
                       "ready label", "destructive-safety"):
            self.assertIn(phrase, text, phrase)


LABELS = {"ready": "afk-ready", "done": "afk-done", "blocked": "afk-blocked"}


def pr(number, labels=("afk-ready",), draft=True, files=("cases/x.yaml",)):
    return {"number": number, "headRefName": f"branch-{number}", "isDraft": draft,
            "isCrossRepository": False,
            "labels": [{"name": name} for name in labels],
            "files": [{"path": path} for path in files]}


def labeled(login, at, label="afk-ready", kind="labeled", actor_type="User"):
    return {"event": kind, "created_at": at, "label": {"name": label},
            "actor": {"login": login, "type": actor_type}}


class SelectReadyPrsTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module("bin/lib/select_ready_prs.py", "select_ready_prs")

    def classify(self, item, events, comments=(), others=(), night_actor=""):
        return self.mod.classify(item, list(events), list(comments), list(others),
                                 LABELS, r"\[bot\]$", night_actor)

    def test_human_label_is_eligible(self):
        self.assertEqual(self.classify(pr(1), [labeled("alex", "2026-10-23T10:00:00Z")]),
                         ("eligible", ""))

    def test_bot_label_is_skipped(self):
        status, reason = self.classify(pr(1), [labeled("ci[bot]", "2026-10-23T10:00:00Z", actor_type="Bot")])
        self.assertEqual(status, "skipped")
        self.assertIn("ci[bot]", reason)

    def test_night_actor_label_is_skipped(self):
        status, _ = self.classify(pr(1), [labeled("night", "2026-10-23T10:00:00Z")], night_actor="night")
        self.assertEqual(status, "skipped")

    def test_unlabeled_after_labeled_is_skipped(self):
        events = [labeled("alex", "2026-10-23T10:00:00Z"),
                  labeled("alex", "2026-10-23T11:00:00Z", kind="unlabeled")]
        self.assertEqual(self.classify(pr(1), events)[0], "skipped")

    def test_not_draft_and_done_and_blocked_are_skipped(self):
        event = [labeled("alex", "2026-10-23T10:00:00Z")]
        self.assertEqual(self.classify(pr(1, draft=False), event)[0], "skipped")
        self.assertEqual(self.classify(pr(1, labels=("afk-ready", "afk-done")), event)[0], "skipped")
        self.assertEqual(self.classify(pr(1, labels=("afk-ready", "afk-blocked")), event)[0], "skipped")

    def test_report_newer_than_label_is_skipped_older_is_not(self):
        event = [labeled("alex", "2026-10-23T10:00:00Z")]
        newer = [{"body": "### Night shift - night-shift run 1", "created_at": "2026-10-23T12:00:00Z"}]
        older = [{"body": "### Night shift - night-shift run 0", "created_at": "2026-10-22T12:00:00Z"}]
        self.assertEqual(self.classify(pr(1), event, newer)[0], "skipped")
        self.assertEqual(self.classify(pr(1), event, older)[0], "eligible")

    def test_file_shared_with_other_open_pr_is_skipped(self):
        event = [labeled("alex", "2026-10-23T10:00:00Z")]
        other = pr(2, labels=(), files=("framework/drivers/files.py",))
        status, reason = self.classify(pr(1, files=("framework/drivers/files.py",)), event, others=[other])
        self.assertEqual(status, "skipped")
        self.assertIn("framework/drivers/files.py", reason)

    def test_load_json_items_reads_array_and_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            array = Path(tmp) / "a.json"
            lines = Path(tmp) / "b.json"
            array.write_text('[{"x": 1}, {"x": 2}]', encoding="utf-8")
            lines.write_text('{"x": 1}\n{"x": 2}\n', encoding="utf-8")
            self.assertEqual(self.mod.load_json_items(array), [{"x": 1}, {"x": 2}])
            self.assertEqual(self.mod.load_json_items(lines), [{"x": 1}, {"x": 2}])
            self.assertEqual(self.mod.load_json_items(Path(tmp) / "missing.json"), [])

    def test_cli_prints_eligible_and_reports_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "prs.json").write_text(json.dumps([pr(12), pr(13, files=("b.yaml",))]), encoding="utf-8")
            (tmp / "12.events.json").write_text(json.dumps([labeled("alex", "2026-10-23T10:00:00Z")]), encoding="utf-8")
            (tmp / "13.events.json").write_text(json.dumps([labeled("ci[bot]", "2026-10-23T10:00:00Z", actor_type="Bot")]), encoding="utf-8")
            for number in (12, 13):
                (tmp / f"{number}.comments.json").write_text("[]", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "bin/lib/select_ready_prs.py"), "--prs", str(tmp / "prs.json"),
                 "--events-dir", str(tmp), "--label-ready", "afk-ready", "--label-done", "afk-done",
                 "--label-blocked", "afk-blocked"],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "12\tbranch-12")
        self.assertIn("skip #13:", result.stderr)

    def test_cli_help(self):
        result = subprocess.run([sys.executable, str(ROOT / "bin/lib/select_ready_prs.py"), "--help"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout.lower())


class SelectReadyPrsFailClosedTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module("bin/lib/select_ready_prs.py", "select_ready_prs")

    def classify(self, item, events, comments=(), night_actor=""):
        return self.mod.classify(item, list(events), list(comments), [], LABELS, r"\[bot\]$", night_actor)

    def test_label_event_without_created_at_is_skipped(self):
        event = labeled("alex", "2026-10-23T10:00:00Z")
        del event["created_at"]
        self.assertEqual(self.classify(pr(1), [event])[0], "skipped")
        event["created_at"] = ""
        self.assertEqual(self.classify(pr(1), [event])[0], "skipped")

    def test_actor_null_or_without_login_is_skipped(self):
        null_actor = labeled("alex", "2026-10-23T10:00:00Z")
        null_actor["actor"] = None
        no_login = labeled("alex", "2026-10-23T10:00:00Z")
        no_login["actor"] = {"type": "User"}
        self.assertEqual(self.classify(pr(1), [null_actor])[0], "skipped")
        self.assertEqual(self.classify(pr(1), [no_login])[0], "skipped")

    def test_report_without_created_at_is_skipped(self):
        event = [labeled("alex", "2026-10-23T10:00:00Z")]
        for comment in ({"body": "night-shift run 1"},
                        {"body": "night-shift run 1", "created_at": ""},
                        {"body": "night-shift run 1", "created_at": None}):
            self.assertEqual(self.classify(pr(1), event, [comment])[0], "skipped")

    def test_report_at_exactly_label_time_is_skipped(self):
        event = [labeled("alex", "2026-10-23T10:00:00Z")]
        tie = [{"body": "night-shift run 1", "created_at": "2026-10-23T10:00:00Z"}]
        self.assertEqual(self.classify(pr(1), event, tie)[0], "skipped")

    def test_night_actor_comparison_ignores_case(self):
        status, _ = self.classify(pr(1), [labeled("Night", "2026-10-23T10:00:00Z")], night_actor="night")
        self.assertEqual(status, "skipped")


class SelectReadyPrsCliFailClosedTests(unittest.TestCase):
    def run_cli(self, tmp, *extra, prs=None):
        prs_path = Path(tmp) / "prs.json"
        if prs is not None:
            prs_path.write_text(json.dumps(prs), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(ROOT / "bin/lib/select_ready_prs.py"), "--prs", str(prs_path),
             "--events-dir", str(tmp), "--label-ready", "afk-ready", "--label-done", "afk-done",
             "--label-blocked", "afk-blocked", *extra],
            capture_output=True, text=True, check=False)

    def write(self, tmp, number, events=True, comments=True, events_text=None):
        good = json.dumps([labeled("alex", "2026-10-23T10:00:00Z")])
        if events:
            (Path(tmp) / f"{number}.events.json").write_text(events_text or good, encoding="utf-8")
        if comments:
            (Path(tmp) / f"{number}.comments.json").write_text("[]", encoding="utf-8")

    def test_missing_comments_file_skips_the_pr(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, 12, comments=False)
            result = self.run_cli(tmp, prs=[pr(12)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("skip #12:", result.stderr)

    def test_missing_events_file_skips_the_pr(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, 12, events=False)
            result = self.run_cli(tmp, prs=[pr(12)])
        self.assertEqual(result.stdout, "")
        self.assertIn("skip #12:", result.stderr)

    def test_empty_files_are_valid_but_not_eligible(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, 12, events_text="")
            (Path(tmp) / "12.events.json").write_text("", encoding="utf-8")
            result = self.run_cli(tmp, prs=[pr(12)])
        self.assertEqual(result.stdout, "")
        self.assertIn("skip #12:", result.stderr)
        self.assertNotIn("not fetched", result.stderr)

    def test_malformed_json_skips_only_that_pr(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, 12, events_text='{"event": "labeled"}\n{not json}\n')
            self.write(tmp, 13)
            result = self.run_cli(tmp, prs=[pr(12, files=("a.yaml",)), pr(13, files=("b.yaml",))])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "13\tbranch-13")
        self.assertIn("skip #12: unreadable data", result.stderr)

    def test_record_without_number_is_skipped_not_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, 13)
            result = self.run_cli(tmp, prs=[{"headRefName": "x", "labels": [{"name": "afk-ready"}]}, pr(13)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "13\tbranch-13")
        self.assertIn("skip #?: unreadable data", result.stderr)

    def test_only_limits_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, 12)
            self.write(tmp, 13)
            result = self.run_cli(tmp, "--only", "13", prs=[pr(12, files=("a.yaml",)), pr(13, files=("b.yaml",))])
        self.assertEqual(result.stdout.strip(), "13\tbranch-13")

    def test_missing_prs_file_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli(tmp)
        self.assertEqual(result.returncode, 2)
        self.assertIn("select_ready_prs: cannot read PR list:", result.stderr)


FAKE_GH = """#!/usr/bin/env bash
# Answers like the real gh: `api ... --jq '.[]'` prints one JSON object per line.
# Every call is recorded as one JSON array per line in $FIXTURES/gh-calls.jsonl.
python3 -c 'import json, sys; print(json.dumps(sys.argv[1:]))' "$@" >> "$FIXTURES/gh-calls.jsonl"
case "$1 $2" in
  "pr list") cat "$FIXTURES/prs.json" ;;
  "pr view")
    # `pr view <n> --json labels --jq '.labels[].name'`: one label name per line;
    # $FIXTURES/<n>.labels (written by a fake session) overrides prs.json.
    if [ -f "$FIXTURES/$3.labels" ]; then cat "$FIXTURES/$3.labels"
    else
      python3 -c 'import json, sys; [print(l["name"]) for p in json.load(open(sys.argv[1])) if str(p["number"]) == sys.argv[2] for l in p["labels"]]' "$FIXTURES/prs.json" "$3"
    fi ;;
  "pr comment"|"pr edit") [ -z "${FAKE_GH_FAIL_WRITES:-}" ] || exit 1 ;;
  "repo view") printf '%s\\n' "${FAKE_DEFAULT_BRANCH-main}" ;;
  api\ *)
    n=$(printf '%s' "$2" | sed -E 's#.*/issues/([0-9]+)/.*#\\1#')
    case "$2" in
      */events) f="$FIXTURES/$n.events.json" ;;
      */comments) f="$FIXTURES/$n.comments.json" ;;
      *) exit 1 ;;
    esac
    if [ -f "$f" ]; then
      python3 -c 'import json, sys; [print(json.dumps(x)) for x in json.load(open(sys.argv[1]))]' "$f"
    fi ;;
  *) exit 1 ;;
esac
"""

CONTEXT = """# Project Context

## Coverage Pipeline

- labels.ready: afk-ready
- labels.done: afk-done
- labels.blocked: afk-blocked
- night.permission_mode: {mode}
- night.allowed_tools: Read,Edit
- night.max_turns: {turns}
- night.timeout_minutes: {timeout}
- night.actor_login:
"""


def context(mode="acceptEdits", turns="5", timeout="1"):
    return CONTEXT.format(mode=mode, turns=turns, timeout=timeout)


def gh_calls(fixtures):
    path = Path(fixtures) / "gh-calls.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def has_timeout_command():
    return bool(shutil.which("timeout") or shutil.which("gtimeout"))


def write_gh_fixtures(tmp, prs, human_labelled):
    fixtures = tmp / "fixtures"
    fixtures.mkdir(exist_ok=True)
    (fixtures / "prs.json").write_text(prs if isinstance(prs, str) else json.dumps(prs), encoding="utf-8")
    for number in human_labelled:
        (fixtures / f"{number}.events.json").write_text(
            json.dumps([labeled("alex", "2026-10-23T10:00:00Z")]), encoding="utf-8")
    gh = tmp / "gh"
    gh.write_text(FAKE_GH, encoding="utf-8")
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    return fixtures, gh


class QaNightTests(unittest.TestCase):
    def run_night(self, *args, mode="acceptEdits", turns="5", timeout="1", prs=None, extra_env=None):
        tmp = Path(self.tmp.name)
        target = tmp / "target"
        (target / "ai-workflow").mkdir(parents=True, exist_ok=True)
        (target / "ai-workflow" / "project-context.md").write_text(
            context(mode=mode, turns=turns, timeout=timeout), encoding="utf-8")
        if prs is None:
            prs = [pr(12), pr(13, files=("b.yaml",))]
        fixtures, gh = write_gh_fixtures(tmp, prs, human_labelled=(12, 14, 15, 16))
        self.fixtures = fixtures
        (fixtures / "13.events.json").write_text(json.dumps([labeled("ci[bot]", "2026-10-23T10:00:00Z", actor_type="Bot")]), encoding="utf-8")
        env = dict(os.environ, QA_NIGHT_GH=str(gh), QA_NIGHT_HOME=str(tmp / "home"),
                   QA_NIGHT_CLAUDE="false", FIXTURES=str(fixtures))
        env.pop("QA_NIGHT_ALLOW_NO_TIMEOUT", None)
        env.update(extra_env or {})
        return subprocess.run([str(ROOT / "bin/qa-night"), str(target), *args],
                              env=env, capture_output=True, text=True, check=False)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_shell_syntax(self):
        result = subprocess.run(["bash", "-n", str(ROOT / "bin/qa-night")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_help(self):
        result = subprocess.run([str(ROOT / "bin/qa-night"), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("qa-night <target-path>", result.stdout)

    def test_requires_target(self):
        result = subprocess.run([str(ROOT / "bin/qa-night")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("target path is required", result.stderr)

    def test_dry_run_selects_human_labelled_pr_only(self):
        result = self.run_night("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would run: #12 (branch-12)", result.stdout)
        self.assertNotIn("#13", result.stdout)
        self.assertIn("skip #13:", result.stderr)

    def test_once_limits_to_one_pr(self):
        result = self.run_night("--dry-run", "--once", "13")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("nothing to do", result.stdout)

    def test_dry_run_once_selects_only_that_pr(self):
        result = self.run_night("--dry-run", "--once", "12")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would run: #12 (branch-12)", result.stdout)
        self.assertNotIn("#13", result.stdout + result.stderr)

    def test_once_requires_a_pr_number(self):
        for args in (("--dry-run", "--once", "abc"), ("--dry-run", "--once", ""), ("--dry-run", "--once")):
            with self.subTest(args=args):
                result = self.run_night(*args)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("qa-night: --once needs a PR number", result.stderr)

    def test_refuses_bypass_permissions(self):
        result = self.run_night("--dry-run", mode="bypassPermissions")
        self.assertEqual(result.returncode, 1)
        self.assertIn("bypassPermissions is not allowed", result.stderr)

    def assert_rejected_before_gh(self, result, message):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)
        self.assertNotIn("would run", result.stdout)
        self.assertEqual(gh_calls(self.fixtures), [])

    def test_refuses_bypass_permissions_in_any_casing(self):
        for mode in ("bypassPermissions", "BypassPermissions", "bypasspermissions", "BYPASSPERMISSIONS"):
            with self.subTest(mode=mode):
                result = self.run_night("--dry-run", mode=mode)
                self.assert_rejected_before_gh(result, "bypassPermissions is not allowed")

    def test_rejects_unknown_permission_mode(self):
        for mode in ("auto", "AcceptEdits"):
            with self.subTest(mode=mode):
                result = self.run_night("--dry-run", mode=mode)
                self.assert_rejected_before_gh(
                    result, "qa-night: night.permission_mode must be one of default, acceptEdits, plan, dontAsk")

    def test_rejects_non_numeric_timeout(self):
        for timeout in ("10m", "abc", "-5", "1.5", "0"):
            with self.subTest(timeout=timeout):
                result = self.run_night("--dry-run", timeout=timeout)
                self.assert_rejected_before_gh(
                    result, "qa-night: night.timeout_minutes must be a whole number greater than 0")

    def test_rejects_zero_or_non_numeric_max_turns(self):
        for turns in ("0", "00", "many"):
            with self.subTest(turns=turns):
                result = self.run_night("--dry-run", turns=turns)
                self.assert_rejected_before_gh(
                    result, "qa-night: night.max_turns must be a whole number greater than 0")

    def test_dry_run_skips_fork_default_branch_and_unsafe_branch(self):
        fork = dict(pr(14, files=("c.yaml",)), isCrossRepository=True)
        default = dict(pr(15, files=("d.yaml",)), headRefName="main")
        unsafe = dict(pr(16, files=("e.yaml",)), headRefName="feat&rm -rf")
        result = self.run_night("--dry-run", prs=[pr(12), fork, default, unsafe])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would run: #12 (branch-12)", result.stdout)
        for number in ("#14", "#15", "#16"):
            self.assertNotIn(number, result.stdout)
        self.assertIn("skip #14: PR from a fork", result.stderr)
        self.assertIn("skip #15: head is the default branch", result.stderr)
        self.assertIn("skip #16: unsafe branch name", result.stderr)

    def test_unknown_default_branch_runs_nothing(self):
        result = self.run_night("--dry-run", extra_env={"FAKE_DEFAULT_BRANCH": ""})
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("would run", result.stdout)
        self.assertIn("cannot determine the default branch", result.stderr)

    def test_selector_failure_is_reported(self):
        result = self.run_night("--dry-run", prs="not json")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("select_ready_prs: cannot read PR list:", result.stderr)
        self.assertNotIn("would run", result.stdout)
        self.assertNotIn("nothing to do", result.stdout)

    @unittest.skipIf(has_timeout_command(), "a timeout command is installed")
    def test_refuses_real_run_without_timeout(self):
        result = self.run_night()
        self.assertEqual(result.returncode, 1)
        self.assertIn("qa-night: no timeout command found (brew install coreutils for gtimeout); "
                      "set QA_NIGHT_ALLOW_NO_TIMEOUT=1 to run without a time limit", result.stderr)
        self.assertNotIn("->", result.stdout)


FAKE_CLAUDE = """#!/usr/bin/env bash
set -e
branch=$(git rev-parse --abbrev-ref HEAD)
# argv, NUL-separated, for the permission assertions
printf '%s\\0' "$@" > "$RECORD/$branch.argv"
prompt=""
while [ $# -gt 0 ]; do
  case "$1" in -p) prompt="$2"; shift ;; esac
  shift
done
printf '%s' "$prompt" > "$RECORD/$branch.prompt"
echo "fake claude ran on $branch"
echo night > night.txt
git add night.txt
git commit -q -m "night-shift run test"
case "$branch" in push-*) git push -q origin "$branch" ;; esac
# FAKE_CLAUDE_SWAP_LABELS: the session itself swapped ready for blocked.
if [ -n "${FAKE_CLAUDE_SWAP_LABELS:-}" ]; then
  printf 'afk-blocked\\n' > "$FIXTURES/${branch##*-}.labels"
fi
exit "${FAKE_CLAUDE_EXIT:-0}"
"""


class QaNightLaunchLoopTests(unittest.TestCase):
    """Runs the real launch loop against a throwaway repository and bare origin."""

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd, env=self.env, capture_output=True,
                              text=True, check=True).stdout

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        tmp = Path(self.tmp.name)
        (tmp / "gitconfig").write_text("", encoding="utf-8")
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=str(tmp / "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
        self.env.pop("QA_NIGHT_ALLOW_NO_TIMEOUT", None)
        self.origin = tmp / "origin.git"
        self.git("init", "-q", "--bare", "-b", "main", str(self.origin))
        seed = tmp / "seed"
        self.git("init", "-q", "-b", "main", str(seed))
        (seed / "README").write_text("seed\n", encoding="utf-8")
        self.git("add", "README", cwd=seed)
        self.git("commit", "-q", "-m", "seed", cwd=seed)
        self.git("remote", "add", "origin", str(self.origin), cwd=seed)
        self.git("push", "-q", "origin", "main", cwd=seed)
        for branch in ("push-21", "keep-22", "diverge-24"):
            self.git("checkout", "-q", "-b", branch, "main", cwd=seed)
            (seed / f"{branch}.txt").write_text(branch, encoding="utf-8")
            self.git("add", f"{branch}.txt", cwd=seed)
            self.git("commit", "-q", "-m", branch, cwd=seed)
            self.git("push", "-q", "origin", branch, cwd=seed)
        self.target = tmp / "target"
        self.git("clone", "-q", str(self.origin), str(self.target))
        (self.target / "ai-workflow").mkdir()
        (self.target / "ai-workflow" / "project-context.md").write_text(
            context(), encoding="utf-8")
        self.git("branch", "-q", "diverge-24", "origin/diverge-24", cwd=self.target)
        self.git("worktree", "add", "-q", str(tmp / "local-24"), "diverge-24", cwd=self.target)
        (tmp / "local-24" / "local.txt").write_text("local only", encoding="utf-8")
        self.git("add", "local.txt", cwd=tmp / "local-24")
        self.git("commit", "-q", "-m", "local only", cwd=tmp / "local-24")
        self.git("worktree", "remove", str(tmp / "local-24"), cwd=self.target)

        def branch_pr(number, branch):
            return dict(pr(number, files=(f"{number}.yaml",)), headRefName=branch)

        prs = [branch_pr(21, "push-21"), branch_pr(22, "keep-22"),
               branch_pr(23, "feat&x"), branch_pr(24, "diverge-24")]
        fixtures, gh = write_gh_fixtures(tmp, prs, human_labelled=(21, 22, 23, 24))
        self.fixtures = fixtures
        claude = tmp / "claude"
        claude.write_text(FAKE_CLAUDE, encoding="utf-8")
        claude.chmod(claude.stat().st_mode | stat.S_IEXEC)
        self.record = tmp / "record"
        self.record.mkdir()
        self.home = tmp / "home"
        self.env.update(QA_NIGHT_GH=str(gh), QA_NIGHT_CLAUDE=str(claude), QA_NIGHT_HOME=str(self.home),
                        FIXTURES=str(fixtures), RECORD=str(self.record))
        if not has_timeout_command():
            self.env["QA_NIGHT_ALLOW_NO_TIMEOUT"] = "1"

    def tearDown(self):
        self.tmp.cleanup()

    def test_launch_loop(self):
        result = subprocess.run([str(ROOT / "bin/qa-night"), str(self.target)], env=self.env,
                                capture_output=True, text=True, check=False)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 1, output)
        runs = list((self.home / "runs").iterdir())
        self.assertEqual(len(runs), 1, runs)
        run_dir = runs[0]

        # (a) committed and pushed: log written, worktree removed, commit on origin
        self.assertIn("fake claude ran on push-21", (run_dir / "pr-21.log").read_text())
        self.assertFalse((run_dir / "wt-21").exists(), output)
        self.assertIn("#21 finished (exit 0), worktree removed", result.stdout)
        self.assertIn("night-shift run test", self.git("log", "--format=%s", "push-21", cwd=self.origin))
        prompt = (self.record / "push-21.prompt").read_text()
        self.assertIn("pull request #21 (branch push-21)", prompt)
        self.assertIn(f"{self.target}/ai-workflow/project-context.md", prompt)
        self.assertNotIn("{{", prompt)

        # (b) committed without pushing: worktree kept, non-zero exit
        self.assertTrue((run_dir / "wt-22").is_dir(), output)
        self.assertIn(f"#22 left unpushed work, worktree kept: {run_dir}/wt-22", result.stderr)

        # unsafe branch name: skipped before any git call, the others still ran
        self.assertIn("skip #23: unsafe branch name", result.stderr)
        self.assertFalse((run_dir / "pr-23.log").exists())

        # local branch diverging from origin: skipped, not reset
        self.assertIn("skip #24: local branch diverges from origin", result.stderr)
        self.assertFalse((run_dir / "wt-24").exists())
        self.assertFalse((self.record / "diverge-24.prompt").exists())
        self.assertIn("local only", self.git("log", "--format=%s", "diverge-24", cwd=self.target))


    def run_once(self, number, **extra_env):
        env = dict(self.env, **extra_env)
        result = subprocess.run([str(ROOT / "bin/qa-night"), str(self.target), "--once", str(number)],
                                env=env, capture_output=True, text=True, check=False)
        runs = list((self.home / "runs").iterdir())
        self.assertEqual(len(runs), 1, runs)
        return result, runs[0]

    def option_values(self, argv, option):
        start = argv.index(option) + 1
        end = start
        while end < len(argv) and not argv[end].startswith("--"):
            end += 1
        return argv[start:end]

    def write_calls(self):
        return [call for call in gh_calls(self.fixtures) if call[:2] in (["pr", "comment"], ["pr", "edit"])]

    def test_session_gets_deny_rules_and_context_read_rule(self):
        result, _ = self.run_once(21)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        argv = (self.record / "push-21.argv").read_text().split("\0")[:-1]
        deny = self.option_values(argv, "--disallowedTools")
        kit = str(ROOT)
        for rule in ("Bash(gh pr merge:*)", "Bash(gh pr ready:*)", "Bash(gh pr review:*)",
                     "Bash(gh pr close:*)", "Bash(gh api:*)", "Bash(git push --force:*)",
                     "Bash(git push -f:*)", "Bash(git push --force-with-lease:*)",
                     "Bash(git push origin HEAD:main)", f"Edit(/{kit}/**)", f"Write(/{kit}/**)"):
            self.assertIn(rule, deny, rule)
        self.assertTrue(f"Edit(/{kit}/**)".startswith("Edit(//"))
        allow = self.option_values(argv, "--allowedTools")
        self.assertIn("Read,Edit", allow)
        self.assertIn(f"Read(/{self.target}/ai-workflow/project-context.md)", allow)
        self.assertEqual(self.option_values(argv, "--add-dir"), [kit])
        self.assertEqual(self.write_calls(), [])

    def test_failed_session_is_reported_as_budget_and_blocked(self):
        result, run_dir = self.run_once(21, FAKE_CLAUDE_EXIT="124")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        calls = gh_calls(self.fixtures)
        self.assertIn(["pr", "view", "21", "--json", "labels", "--jq", ".labels[].name"], calls)
        comments = [call for call in calls if call[:3] == ["pr", "comment", "21"]]
        self.assertEqual(len(comments), 1, calls)
        body = comments[0][comments[0].index("--body") + 1]
        self.assertTrue(body.startswith(f"### Night shift - night-shift run {run_dir.name}"), body)
        self.assertIn("**Status:** blocked", body)
        self.assertIn("**Blocked on:** budget - session ended with exit 124 before reporting; "
                      f"see log {run_dir}/pr-21.log", body)
        self.assertIn(["pr", "edit", "21", "--remove-label", "afk-ready", "--add-label", "afk-blocked"], calls)
        self.assertLess(calls.index(comments[0]),
                        calls.index(["pr", "edit", "21", "--remove-label", "afk-ready", "--add-label", "afk-blocked"]))

    def test_failed_session_that_swapped_labels_itself_issues_nothing(self):
        result, _ = self.run_once(21, FAKE_CLAUDE_EXIT="3", FAKE_CLAUDE_SWAP_LABELS="1")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(["pr", "view", "21", "--json", "labels", "--jq", ".labels[].name"], gh_calls(self.fixtures))
        self.assertEqual(self.write_calls(), [])

    def test_successful_session_that_swapped_labels_issues_nothing(self):
        result, _ = self.run_once(21, FAKE_CLAUDE_SWAP_LABELS="1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([c for c in gh_calls(self.fixtures) if c[:2] == ["pr", "view"]], [])
        self.assertEqual(self.write_calls(), [])

    def test_failed_budget_report_is_logged_and_run_continues(self):
        result, _ = self.run_once(21, FAKE_CLAUDE_EXIT="124", FAKE_GH_FAIL_WRITES="1")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("qa-night: #21 could not post the budget report", result.stderr)
        self.assertIn("#21 finished (exit 124), worktree removed", result.stdout)


if __name__ == "__main__":
    unittest.main()
