import importlib.util
import json
import os
import re
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


def pr(number, labels=("afk-ready",), draft=True, files=("catalog/x.yaml",)):
    return {"number": number, "headRefName": f"branch-{number}", "isDraft": draft,
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


if __name__ == "__main__":
    unittest.main()
