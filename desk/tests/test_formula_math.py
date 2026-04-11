import unittest
import sys
from pathlib import Path

DESK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DESK))

from formula import list_math_in_markdown  # noqa: E402


class TestListMath(unittest.TestCase):
    def test_display_only(self):
        text = r"intro $$\alpha + 1$$ tail"
        items = list_math_in_markdown(text)
        self.assertEqual(items, [("display", r"\alpha + 1")])

    def test_inline_only(self):
        text = r"value is $\sigma_\psi{=}5$ here"
        items = list_math_in_markdown(text)
        self.assertEqual(items, [("inline", r"\sigma_\psi{=}5")])

    def test_display_then_inline_order(self):
        text = r"$$R=a$$ then $\psi$ ok"
        items = list_math_in_markdown(text)
        self.assertEqual(
            items,
            [("display", "R=a"), ("inline", r"\psi")],
        )

    def test_inline_not_inside_display(self):
        text = r"$$ x = $bad$ $$ outer $\psi$ end"
        items = list_math_in_markdown(text)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0][0], "display")
        self.assertIn("$bad$", items[0][1])
        self.assertEqual(items[1], ("inline", r"\psi"))


if __name__ == "__main__":
    unittest.main()
