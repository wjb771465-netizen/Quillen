import sys
import unittest
from pathlib import Path

DESK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DESK))

from formula import _body_after_yaml_front_matter, _source_stem  # noqa: E402


class TestBodyAfterYamlFrontMatter(unittest.TestCase):
    def test_no_front_matter(self):
        text = "hello $x$ world"
        self.assertEqual(_body_after_yaml_front_matter(text), text)

    def test_strips_front_matter(self):
        text = "---\nfoo: bar\n---\n\nbody $\\alpha$\n"
        self.assertEqual(_body_after_yaml_front_matter(text), "\nbody $\\alpha$\n")

    def test_unclosed_front_matter_returns_full(self):
        text = "---\nfoo: bar\n\nno closing\n$x$"
        self.assertEqual(_body_after_yaml_front_matter(text), text)


class TestSourceStem(unittest.TestCase):
    def test_qpad_double_suffix(self):
        self.assertEqual(_source_stem(Path("handoff-sample.qpad.md")), "handoff-sample")

    def test_plain_md(self):
        self.assertEqual(_source_stem(Path("note.md")), "note")


if __name__ == "__main__":
    unittest.main()
