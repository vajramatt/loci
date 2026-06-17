"""Version reporting — no SDK, no network.

`// help` and `loci version` surface loci.version_string(); these lock in its
shape and the build-stamp precedence so a friend's bug report names an exact
build.
"""

import re
import sys
import types
import unittest

import loci


class VersionStringTests(unittest.TestCase):
    def test_starts_with_semver(self):
        self.assertTrue(loci.version_string().startswith(loci.__version__))

    def test_shape_is_semver_or_semver_with_commit(self):
        vs = loci.version_string()
        ok = vs == loci.__version__ or re.fullmatch(
            re.escape(loci.__version__) + r" \(\S+\)", vs
        )
        self.assertTrue(ok, f"unexpected version string: {vs!r}")

    def test_commit_is_str_or_none(self):
        self.assertIsInstance(loci._commit(), (str, type(None)))

    def test_build_stamp_wins_over_live_git(self):
        # install.sh writes loci/_commit.py; it must take precedence over any
        # ambient `git` lookup so installed builds report what was stamped.
        stamp = types.ModuleType("loci._commit")
        stamp.COMMIT = "deadbee"
        sys.modules["loci._commit"] = stamp
        try:
            self.assertEqual(loci._commit(), "deadbee")
            self.assertEqual(
                loci.version_string(), f"{loci.__version__} (deadbee)"
            )
        finally:
            del sys.modules["loci._commit"]


if __name__ == "__main__":
    unittest.main()
