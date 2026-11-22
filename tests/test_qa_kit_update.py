import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True,
                          text=True, check=True, env={**os.environ, **GIT_ENV}).stdout.strip()


class QaKitSelfUpdateTests(unittest.TestCase):
    """bin/qa-kit fast-forwards the kit's main before launching, never blocking."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        seed = base / "seed"
        (seed / "bin").mkdir(parents=True)
        shutil.copy(ROOT / "bin" / "qa-kit", seed / "bin" / "qa-kit")
        (seed / "notes.txt").write_text("v1\n", encoding="utf-8")
        git(base, "init", "-q", "-b", "main", str(seed))
        git(seed, "add", ".")
        git(seed, "commit", "-q", "-m", "v1")
        self.origin = base / "origin.git"
        git(base, "clone", "-q", "--bare", str(seed), str(self.origin))
        self.kit = base / "kit"
        git(base, "clone", "-q", str(self.origin), str(self.kit))
        # Upstream moves ahead: a new launcher version and a changed note.
        launcher = seed / "bin" / "qa-kit"
        text = launcher.read_text(encoding="utf-8")
        launcher.write_text(text.replace("set -euo pipefail\n",
                                         "set -euo pipefail\necho 'NEW VERSION' >&2\n", 1),
                            encoding="utf-8")
        (seed / "notes.txt").write_text("v2\n", encoding="utf-8")
        git(seed, "commit", "-q", "-am", "v2")
        git(seed, "push", "-q", str(self.origin), "main")
        self.upstream = git(self.origin, "rev-parse", "main")

        self.target = base / "target"
        (self.target / "ai-workflow").mkdir(parents=True)
        (self.target / "ai-workflow" / "project-context.md").write_text("# ctx\n", encoding="utf-8")
        fake = base / "fakebin"
        fake.mkdir()
        (fake / "claude").write_text("#!/bin/sh\necho LAUNCHED\n", encoding="utf-8")
        (fake / "claude").chmod(0o755)
        self.path = f"{fake}{os.pathsep}{os.environ['PATH']}"

    def tearDown(self):
        self.tmp.cleanup()

    def launch(self, **env):
        run_env = {**os.environ, **GIT_ENV, "PATH": self.path}
        run_env.pop("QA_KIT_NO_UPDATE", None)
        run_env.pop("QA_KIT_UPDATED", None)
        run_env.update(env)
        return subprocess.run(["bash", str(self.kit / "bin" / "qa-kit"), str(self.target)],
                              capture_output=True, text=True, check=False, env=run_env)

    def test_behind_and_clean_fast_forwards_and_restarts_new_version(self):
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("LAUNCHED", result.stdout)
        self.assertIn("kit updated", result.stderr)
        self.assertIn("NEW VERSION", result.stderr)
        self.assertEqual(git(self.kit, "rev-parse", "HEAD"), self.upstream)

    def test_unrelated_local_edit_still_fast_forwards(self):
        (self.kit / "local.txt").write_text("mine\n", encoding="utf-8")
        result = self.launch()
        self.assertIn("LAUNCHED", result.stdout)
        self.assertEqual(git(self.kit, "rev-parse", "HEAD"), self.upstream)
        self.assertTrue((self.kit / "local.txt").exists())

    def test_conflicting_local_edit_warns_and_launches_unchanged(self):
        (self.kit / "notes.txt").write_text("my edit\n", encoding="utf-8")
        before = git(self.kit, "rev-parse", "HEAD")
        result = self.launch()
        self.assertIn("LAUNCHED", result.stdout)
        self.assertIn("local edits block", result.stderr)
        self.assertEqual(git(self.kit, "rev-parse", "HEAD"), before)
        self.assertEqual((self.kit / "notes.txt").read_text(encoding="utf-8"), "my edit\n")

    def test_unreachable_origin_warns_and_launches(self):
        git(self.kit, "remote", "set-url", "origin", str(self.origin) + "-missing")
        before = git(self.kit, "rev-parse", "HEAD")
        result = self.launch()
        self.assertIn("LAUNCHED", result.stdout)
        self.assertIn("could not reach origin", result.stderr)
        self.assertEqual(git(self.kit, "rev-parse", "HEAD"), before)

    def test_feature_branch_is_not_updated(self):
        git(self.kit, "switch", "-q", "-c", "feature/x")
        before = git(self.kit, "rev-parse", "HEAD")
        result = self.launch()
        self.assertIn("LAUNCHED", result.stdout)
        self.assertIn("not main", result.stderr)
        self.assertEqual(git(self.kit, "rev-parse", "HEAD"), before)

    def test_opt_out(self):
        before = git(self.kit, "rev-parse", "HEAD")
        result = self.launch(QA_KIT_NO_UPDATE="1")
        self.assertIn("LAUNCHED", result.stdout)
        self.assertNotIn("kit updated", result.stderr)
        self.assertEqual(git(self.kit, "rev-parse", "HEAD"), before)


if __name__ == "__main__":
    unittest.main()
