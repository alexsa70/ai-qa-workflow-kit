import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def skill_names():
    return sorted(path.name for path in SKILLS.iterdir() if path.is_dir())


def frontmatter(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}
    values = {}
    for line in lines[1:]:
        if line == "---":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


class SkillMetadataTests(unittest.TestCase):
    def test_every_skill_has_valid_shared_and_platform_metadata(self):
        names = skill_names()
        self.assertGreater(len(names), 0)
        for name in names:
            skill = SKILLS / name
            shared = frontmatter(skill / "SKILL.md")
            self.assertEqual(name, shared.get("name"), name)
            self.assertTrue(shared.get("description"), name)

            openai = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
            claude = (skill / "agents" / "claude.yaml").read_text(encoding="utf-8")
            for metadata in (openai, claude):
                self.assertIn("interface:", metadata, name)
                self.assertIn("display_name:", metadata, name)
                self.assertIn("short_description:", metadata, name)
                self.assertIn("default_prompt:", metadata, name)
                self.assertIn(name, metadata, name)

            def interface_value(text, key):
                for line in text.splitlines():
                    if line.strip().startswith(f"{key}:"):
                        return line.split(":", 1)[1].strip().strip('"')
                return None

            self.assertEqual(
                interface_value(openai, "display_name"),
                interface_value(claude, "display_name"),
                name,
            )
            self.assertEqual(
                interface_value(openai, "short_description"),
                interface_value(claude, "short_description"),
                name,
            )

    def test_readme_lists_every_skill(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for name in skill_names():
            self.assertIn(f"{name}/", readme, name)


class DocumentationConsistencyTests(unittest.TestCase):
    def test_launcher_and_kit_only_docs_use_project_context(self):
        launcher = (ROOT / "bin" / "qa-kit").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "kit-only-mode.md").read_text(encoding="utf-8")
        for text in (launcher, docs):
            self.assertIn("project-context.md", text)
            self.assertIn("authority order", text)
            self.assertNotIn("/Users/alexanderle/", text)
            self.assertNotIn("backend-код выше runtime", text)

        self.assertIn('TARGET="${1:-${QA_KIT_TARGET:-}}"', launcher)
        self.assertIn("target path is required", launcher)


class ScriptSmokeTests(unittest.TestCase):
    def run_script(self, relative_path, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / relative_path), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_python_scripts_show_help(self):
        scripts = [
            "skills/coverage-matrix/scripts/build_coverage_matrix.py",
            "skills/test-design/scripts/contract_to_xlsx.py",
            "skills/testmo-csv/scripts/tests_to_testmo_csv.py",
        ]
        for script in scripts:
            result = self.run_script(script, "--help")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("usage:", result.stdout.lower(), script)

    def test_launcher_shell_syntax(self):
        result = subprocess.run(
            ["bash", "-n", str(ROOT / "bin" / "qa-kit")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_launcher_requires_target(self):
        env = os.environ.copy()
        env.pop("QA_KIT_TARGET", None)
        result = subprocess.run(
            [str(ROOT / "bin" / "qa-kit")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("target path is required", result.stderr)

    def test_python_sources_compile_without_writing_cache(self):
        for path in ROOT.rglob("*.py"):
            if ".git" not in path.parts:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")


if __name__ == "__main__":
    unittest.main()
