import io
import unittest

from loci import cli
from loci.memory.session import Session
from loci.ui import UI


def ui_capture():
    return UI(stream=io.StringIO(), color=False)


class ControlTokenTest(unittest.TestCase):
    """help / :new / :forget are handled locally — no API turn."""

    def test_help_renders_locally(self):
        ui = ui_capture()
        handled = cli._handle_control("help", Session(key="t"), ui)
        self.assertTrue(handled)
        out = ui.stream.getvalue()
        self.assertIn("summon", out)
        self.assertIn("run_shell", out)

    def test_help_aliases(self):
        for token in ("help", ":help", "?", "-h", "--help"):
            self.assertTrue(
                cli._handle_control(token, Session(key="t"), ui_capture()),
                msg=f"{token!r} should be handled",
            )

    def test_non_control_passes_through(self):
        self.assertFalse(
            cli._handle_control("how many files are here", Session(key="t"), ui_capture())
        )


if __name__ == "__main__":
    unittest.main()
