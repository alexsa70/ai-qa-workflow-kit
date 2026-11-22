import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "hooks"
QA_WORKTREE = ROOT / "bin" / "qa-worktree"


def git(cwd, *args):
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True, text=True, check=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
    ).stdout.strip()


def make_repo(path, branch="main"):
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", branch)
    git(path, "commit", "-q", "--allow-empty", "-m", "init")
    return path


def run_hook(name, command, cwd):
    payload = json.dumps({"tool_input": {"command": command}, "cwd": str(cwd)})
    return subprocess.run(
        ["bash", str(HOOKS / name)], input=payload, cwd=str(cwd),
        capture_output=True, text=True, check=False,
    )


class BranchNeedsWorktreeTests(unittest.TestCase):
    BLOCKED = [
        "git checkout -b foo",
        "git checkout -B foo origin/main",
        "git -C /some/repo checkout -b a/b/c",
        "git switch -c foo",
        "git switch --create foo",
        "git branch newone",
        "git branch feat/x origin/main",
        "cd /x && git checkout -b foo",
    ]
    ALLOWED = [
        "git checkout main",
        "git checkout -- file.py",
        "git switch release",
        "git branch",
        "git branch -d old",
        "git branch -D old",
        "git branch -m a b",
        "git branch --show-current",
        "git worktree add -b foo ../repo-foo origin/main",
        "git log --oneline",
        'echo "git checkout -b" in docs',
    ]

    def test_in_place_branch_creation_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            for command in self.BLOCKED:
                result = run_hook("branch-needs-worktree.sh", command, tmp)
                self.assertEqual(result.returncode, 2, command)
                self.assertIn("qa-worktree", result.stderr, command)

    def test_other_git_commands_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            for command in self.ALLOWED:
                result = run_hook("branch-needs-worktree.sh", command, tmp)
                self.assertEqual(result.returncode, 0, command)


class TargetRepoResolutionTests(unittest.TestCase):
    """Kit-only mode: the hook cwd is the kit, the command targets another repo."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.session = make_repo(base / "kit", branch="feature/session")
        self.target = make_repo(base / "target")

    def tearDown(self):
        self.tmp.cleanup()

    def test_branch_guard_blocks_commit_into_target_on_main(self):
        result = run_hook("pre-commit-branch-guard.sh",
                          f"git -C {self.target} commit -m x", self.session)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("'main'", result.stderr)

    def test_branch_guard_allows_target_on_feature_branch(self):
        git(self.target, "switch", "-q", "-c", "feature/x")
        result = run_hook("pre-commit-branch-guard.sh",
                          f"git -C {self.target} commit -m x", self.session)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_skill_size_check_inspects_the_target_repo(self):
        skill = self.target / "skills" / "big" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("x\n" * 50, encoding="utf-8")
        git(self.target, "add", str(skill))
        result = subprocess.run(
            ["bash", str(HOOKS / "skill-size-check.sh")],
            input=json.dumps({"tool_input": {"command": f"git -C {self.target} commit -m x"}}),
            cwd=str(self.session), capture_output=True, text=True, check=False,
            env={**os.environ, "SKILL_LINE_CAP": "10"},
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        # Same staged file, but the command targets the session repo: silent.
        result = subprocess.run(
            ["bash", str(HOOKS / "skill-size-check.sh")],
            input=json.dumps({"tool_input": {"command": "git commit -m x"}}),
            cwd=str(self.session), capture_output=True, text=True, check=False,
            env={**os.environ, "SKILL_LINE_CAP": "10"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)


class QaWorktreeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        origin = make_repo(base / "seed")
        (origin / "api").mkdir()
        (origin / "api" / "README.md").write_text("api\n", encoding="utf-8")
        (origin / ".gitignore").write_text(".env\n/api/ai-workflow\n", encoding="utf-8")
        git(origin, "add", ".")
        git(origin, "commit", "-q", "-m", "api")
        self.repo = base / "proj"
        subprocess.run(["git", "clone", "-q", str(origin), str(self.repo)], check=True)
        (self.repo / ".env").write_text("SECRET=1\n", encoding="utf-8")
        context = self.repo / "api" / "ai-workflow" / "project-context.md"
        context.parent.mkdir(parents=True)
        self.root = base / "worktrees"
        context.write_text(
            "# Project Context\n\n"
            f"- Repository root: `{self.repo}/api`\n\n"
            "## Worktrees\n\n"
            f"- Worktree root: `{self.root}`\n"
            "- Worktree name: `{repo}-{slug}`\n"
            "- Link into worktree: `.env`\n"
            "- Copy into worktree: `api/ai-workflow`\n\n"
            "## Other\n\n- Link into worktree: ignored\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *args):
        return subprocess.run(["bash", str(QA_WORKTREE), *args],
                              capture_output=True, text=True, check=False)

    def test_creates_worktree_and_prints_equivalent_target(self):
        result = self.run_script(str(self.repo / "api"), "feat/demo")
        self.assertEqual(result.returncode, 0, result.stderr)
        wt = self.root / "proj-demo"
        self.assertEqual(result.stdout.strip(), str(wt / "api"))
        self.assertEqual(git(wt, "branch", "--show-current"), "feat/demo")
        self.assertEqual(git(wt, "rev-parse", "HEAD"), git(self.repo, "rev-parse", "origin/main"))
        self.assertTrue((wt / ".env").is_symlink())
        copied = (wt / "api" / "ai-workflow" / "project-context.md").read_text(encoding="utf-8")
        self.assertIn(f"`{wt}/api`", copied)
        self.assertNotIn(f"`{self.repo}/api`", copied)
        self.assertFalse((wt / "api" / "ai-workflow").is_symlink())
        self.assertEqual(git(wt, "status", "--porcelain"), "")

    def test_refuses_protected_and_existing_branches(self):
        self.assertNotEqual(self.run_script(str(self.repo), "main").returncode, 0)
        git(self.repo, "branch", "taken")
        self.assertNotEqual(self.run_script(str(self.repo), "taken").returncode, 0)

    def test_help(self):
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stderr)


if __name__ == "__main__":
    unittest.main()
