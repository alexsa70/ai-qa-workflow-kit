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


PIPELINE_SKILLS = ["coverage-backlog"]


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


if __name__ == "__main__":
    unittest.main()
