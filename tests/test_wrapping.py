"""Integration regressions: run with python3 -m unittest discover -s tests -v."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def unwrapped(text):
    # fvextra adds visual continuation markers; they are not source content.
    return "".join(text.replace("⌋", "").replace("↪", "").split())


class WrappingTests(unittest.TestCase):
    def convert(self, command, source, content):
        with tempfile.TemporaryDirectory(prefix="pdf wrapping ") as directory:
            source_path = Path(directory) / source
            source_path.write_text(content, encoding="utf-8")
            result = subprocess.run(
                [str(ROOT / command), str(source_path)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(source_path.with_suffix(".pdf").read_bytes().startswith(b"%PDF-"))
            return subprocess.run(
                ["pdftotext", str(source_path.with_suffix(".pdf")), "-"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout

    def test_long_inline_code_wraps_in_markdown(self):
        # Far wider than a page: wrapping must work inside an inline code span.
        token = "long_identifier_" * 20
        text = self.convert("md2pdf", "inline.md", f"Example: `{token}`.\n")
        self.assertIn(token, unwrapped(text))

    def test_long_saved_notebook_output_wraps(self):
        # Saved outputs take Pandoc's verbatim path rather than the minted path.
        output = "[" + ", ".join(["1234567890.123456789"] * 12) + "]"
        notebook = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [{
                "id": "long-output",
                "cell_type": "code",
                "metadata": {},
                "execution_count": 1,
                "source": ["print(values)"],
                "outputs": [{
                    "output_type": "stream",
                    "name": "stdout",
                    "text": [output + "\n"],
                }],
            }],
        }
        text = self.convert("ipynb2pdf", "output.ipynb", json.dumps(notebook))
        self.assertIn(unwrapped(output), unwrapped(text))


if __name__ == "__main__":
    unittest.main()
