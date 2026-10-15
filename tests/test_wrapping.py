"""Integration regressions: run with python3 -m unittest discover -s tests -v."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def unwrapped(text):
    # fvextra adds visual continuation markers; they are not source content.
    return "".join(text.replace("⌋", "").replace("↪", "").split())


class WrappingTests(unittest.TestCase):
    def convert(self, command, source, content, warning=None):
        with tempfile.TemporaryDirectory(prefix="pdf wrapping ") as directory:
            source_path = Path(directory) / source
            source_path.write_text(content, encoding="utf-8")
            result = subprocess.run(
                [str(ROOT / command), str(source_path), "--strict"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            if warning is not None:
                self.assertIn(warning, result.stderr)
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

    def test_prose_escapes_and_paths_in_both_readers(self):
        source = (
            r"Append an EOS letter '\n' to each example cryptic/English text."
            "\n\n" + r"Other escapes: '\t', '\r', '\b', '\f', '\v', '\x00', '\u0000'."
            "\n\n" + r"Windows path: C:\Users\sam\results.csv."
        )
        notebook = {
            "nbformat": 4, "nbformat_minor": 5, "metadata": {},
            "cells": [{"id": "escapes", "cell_type": "markdown",
                       "metadata": {}, "source": source}],
        }
        for command, name, content in (
            ("md2pdf", "escapes.md", source),
            ("ipynb2pdf", "escapes.ipynb", json.dumps(notebook)),
        ):
            with self.subTest(command=command):
                text = self.convert(command, name, content)
                for escape in (r"\n", r"\t", r"\r", r"\b", r"\f", r"\v", r"\x00", r"\u0000"):
                    self.assertIn(escape, text)
                self.assertIn(r"C:\Users\sam\results.csv", unwrapped(text))

    def test_valid_tex_and_math_survive_prose_protection(self):
        source = r"""\newcommand{\customword}{CUSTOMWORD}

\customword, \textbf{BOLDWORD}, and \v{S}.

Inline math: $\alpha + \beta = \gamma$.

\begin{align*}
y &= x + 1 \\
z &= y + 2
\end{align*}

\begin{pmatrix}1 & 2 \\ 3 & 4\end{pmatrix}
"""
        text = self.convert("md2pdf", "math.md", source)
        self.assertIn("CUSTOMWORD", text)
        self.assertIn("BOLDWORD", text)
        self.assertIn("Š", text)
        self.assertTrue("α" in text or "𝛼" in text, text)
        self.assertNotIn(r"\begin", text)

    def test_unknown_code_language_falls_back_without_losing_content(self):
        source = "KEEPMYCODE = 42"
        notebook = {
            "nbformat": 4, "nbformat_minor": 5,
            "metadata": {"kernelspec": {"name": "not-a-real-kernel",
                         "language": "not-a-real-kernel", "display_name": "Unknown"}},
            "cells": [{"id": "unknown-language", "cell_type": "code",
                       "metadata": {}, "execution_count": None,
                       "source": source, "outputs": []}],
        }
        for command, name, content in (
            ("md2pdf", "unknown.md", f"```not-a-real-kernel\n{source}\n```\n"),
            ("ipynb2pdf", "unknown.ipynb", json.dumps(notebook)),
        ):
            with self.subTest(command=command):
                text = self.convert(command, name, content, warning="rendering as plain text")
                self.assertIn("KEEPMYCODE=42", unwrapped(text))

    def test_inline_delimiters_and_unicode(self):
        # Every original candidate delimiter occurs in this code span.
        token = "{}|!@#^&*-=+0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        text = self.convert("md2pdf", "delimiters.md", f"`{token}`\n\n`𝜆 = {{value}}`\n")
        self.assertIn(token, unwrapped(text))
        self.assertIn("𝜆={value}", unwrapped(text))

    def test_quality_warning_strict_mode_and_retained_failure_logs(self):
        # Deliberately force overflow, independently of font metrics.
        source = "```{=latex}\n" + r"\noindent\hbox to 0pt{\rule{300mm}{1pt}}" + "\n```\n"
        with tempfile.TemporaryDirectory(prefix="pdf diagnostics ") as directory:
            root = Path(directory)
            source_path = root / "overflow.md"
            source_path.write_text(source)
            env = dict(os.environ, TMPDIR=directory)
            output = root / "overflow.pdf"
            args = [str(ROOT / "md2pdf"), str(source_path)]
            normal = subprocess.run(args, env=env, capture_output=True, text=True, timeout=120)
            self.assertEqual(normal.returncode, 0, normal.stdout + normal.stderr)
            self.assertIn("warning:", normal.stderr)
            original = output.read_bytes()
            strict = subprocess.run(args + ["--strict"], env=env, capture_output=True, text=True, timeout=120)
            self.assertNotEqual(strict.returncode, 0)
            self.assertIn("--strict", strict.stderr)
            # A failed conversion must not replace a previous successful PDF.
            self.assertEqual(output.read_bytes(), original)
            self.assertTrue(list(root.glob("tmp.*/document.tex")))
            self.assertTrue(list(root.glob("tmp.*/build.log")))

    def test_real_tex_error_is_reported_and_build_files_are_retained(self):
        with tempfile.TemporaryDirectory(prefix="pdf error ") as directory:
            root = Path(directory)
            source_path = root / "broken.md"
            source_path.write_text("$\\undefinedmathcommand{broken}$\n")
            result = subprocess.run(
                [str(ROOT / "md2pdf"), str(source_path)],
                env=dict(os.environ, TMPDIR=directory),
                capture_output=True, text=True, timeout=120,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Undefined control sequence", result.stderr)
            self.assertIn("full diagnostics:", result.stderr)
            self.assertIn("build files retained at", result.stderr)
            self.assertTrue(list(root.glob("tmp.*/document.tex")))
            self.assertTrue(list(root.glob("tmp.*/build.log")))
            self.assertFalse(source_path.with_suffix(".pdf").exists())

    def test_missing_glyph_warns_and_strict_mode_rejects(self):
        with tempfile.TemporaryDirectory(prefix="pdf glyph ") as directory:
            root = Path(directory)
            source = root / "glyph.md"
            # An unassigned Unicode code point, absent from every font.
            source.write_text("Missing glyph: \u0378.\n", encoding="utf-8")
            args = [str(ROOT / "md2pdf"), str(source)]
            env = dict(os.environ, TMPDIR=directory)
            for options, expected in (([], 0), (["--strict"], 1)):
                with self.subTest(options=options):
                    result = subprocess.run(args + options, env=env, capture_output=True,
                                            text=True, timeout=120)
                    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                    self.assertIn("missing font characters", result.stderr)


if __name__ == "__main__":
    unittest.main()
