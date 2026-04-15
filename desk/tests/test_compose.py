import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

DESK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DESK))

from compose import compose  # noqa: E402
from utils import resolve_reference_doc  # noqa: E402


class TestResolveReferenceDoc(unittest.TestCase):
    def test_existing_template(self):
        with tempfile.TemporaryDirectory() as td:
            ref = Path(td) / "mytpl" / "reference.docx"
            ref.parent.mkdir()
            ref.write_bytes(b"fake")
            with patch("utils.TEMPLATES_ROOT", Path(td)):
                result = resolve_reference_doc("mytpl")
            self.assertEqual(result, ref)

    def test_missing_template_raises(self):
        with tempfile.TemporaryDirectory() as td:
            with patch("utils.TEMPLATES_ROOT", Path(td)):
                with self.assertRaises(FileNotFoundError):
                    resolve_reference_doc("nonexistent")


class TestCompose(unittest.TestCase):
    def _make_md(self, tmp: Path, content: str) -> Path:
        f = tmp / "doc.qpad.md"
        f.write_text(content, encoding="utf-8")
        return f

    def test_no_template_calls_md_to_docx_without_reference(self):
        with tempfile.TemporaryDirectory() as td:
            src = self._make_md(Path(td), "# Hello\n\nno front matter\n")
            outbox = Path(td) / "out"
            with patch("compose.md_to_docx") as mock_convert:
                compose(src, outbox)
            mock_convert.assert_called_once()
            _, _, ref = mock_convert.call_args.args
            self.assertIsNone(ref)

    def test_with_template_passes_reference_doc(self):
        with tempfile.TemporaryDirectory() as td:
            ref = Path(td) / "templates" / "mytemplate" / "reference.docx"
            ref.parent.mkdir(parents=True)
            ref.write_bytes(b"fake")
            src = self._make_md(
                Path(td),
                "---\ntemplate: mytemplate\n---\n\n# Hello\n",
            )
            outbox = Path(td) / "out"
            with patch("utils.TEMPLATES_ROOT", Path(td) / "templates"), \
                 patch("compose.md_to_docx") as mock_convert:
                compose(src, outbox)
            mock_convert.assert_called_once()
            _, _, passed_ref = mock_convert.call_args.args
            self.assertEqual(passed_ref, ref)

    def test_missing_template_raises(self):
        with tempfile.TemporaryDirectory() as td:
            src = self._make_md(
                Path(td),
                "---\ntemplate: ghost\n---\n\n# Hello\n",
            )
            with patch("utils.TEMPLATES_ROOT", Path(td) / "templates"), \
                 self.assertRaises(FileNotFoundError):
                compose(src, Path(td) / "out")


if __name__ == "__main__":
    unittest.main()
