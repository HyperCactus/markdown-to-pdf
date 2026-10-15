# md2pdf and ipynb2pdf

Convert Markdown files and Jupyter notebooks to clean, submission-ready PDFs
from the command line.

```bash
md2pdf report.md
ipynb2pdf analysis.ipynb
```

The generated PDF supports:

- LaTeX math
- Syntax-highlighted code with automatic line wrapping
- Relative images
- Unicode text

For notebooks, saved code-cell outputs and figures are included as well. Run
the notebook before converting it if you want the PDF to contain current
results.

Build files are kept in a temporary directory and removed after a clean build.
Failed builds and builds with quality warnings retain their TeX and logs, and
print the directory path. Use `--keep-build` to retain a successful build too.
Conversion progress is shown as a compact progress bar; detailed Pandoc and
LaTeX output is displayed only when a conversion stage fails.

## Install

`md2pdf` currently supports Linux and WSL.

### 1. Install dependencies

On Ubuntu, Debian, or WSL:

```bash
sudo apt update
sudo apt install \
  pandoc \
  texlive-xetex \
  texlive-latex-extra \
  latexmk \
  python3-pygments \
  fonts-dejavu-core \
  fonts-noto-core
```

Pandoc 3.8 or newer is required.

### 2. Install the scripts

```bash
git clone https://github.com/HyperCactus/markdown-to-pdf.git ~/.local/share/md2pdf
chmod +x ~/.local/share/md2pdf/md2pdf
chmod +x ~/.local/share/md2pdf/ipynb2pdf
mkdir -p ~/.local/bin
ln -sf ~/.local/share/md2pdf/md2pdf ~/.local/bin/md2pdf
ln -sf ~/.local/share/md2pdf/ipynb2pdf ~/.local/bin/ipynb2pdf
```

Ensure `~/.local/bin` is on your `PATH`. Add this to `~/.bashrc` if needed:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell and check the installation:

```bash
source ~/.bashrc
md2pdf --version
ipynb2pdf --version
```

## Usage

Create `report.pdf` beside `report.md`:

```bash
md2pdf report.md
```

Choose a different output path:

```bash
md2pdf report.md -o final.pdf
```

Paths containing spaces are supported:

```bash
md2pdf "My Assignment/report.md" -o "My Assignment/final.pdf"
```

View all options and examples:

```bash
md2pdf --help
```

## Jupyter notebook usage

Create `analysis.pdf` beside `analysis.ipynb`:

```bash
ipynb2pdf analysis.ipynb
```

Choose a different output path:

```bash
ipynb2pdf analysis.ipynb -o report.pdf
```

Notebook markdown, math, syntax-highlighted code cells, text output, and
embedded figures are rendered. The script does not execute notebooks; only
outputs already saved in the `.ipynb` file are included.

Long inline code and saved plain-text outputs wrap to fit the page. Inline
code has no background fill so LaTeX can break it across lines; fenced code
blocks keep their background and frame.

LaTeX environments in Markdown cells (such as `align` and `align*`) are
supported. Standalone math-only environments such as `array`, `matrix`, and
the AMS matrix variants are placed in display math automatically. Oversized
math blocks are scaled down to the printable width. When a cell output contains multiple MIME
representations, the richest supported representation is used, so saved plots
render as figures instead of their plain-text descriptions.

Unicode mathematical characters in code cells are rendered automatically
using Noto Sans Math as a fallback font.

Common programming escapes in prose, such as `'\n'` and `'\t'`, are printed
literally. Undefined standalone TeX commands in prose (for example, segments
of Windows paths) also print literally. Math, commands with arguments, and
explicit TeX blocks continue to be typeset as LaTeX. Use backticks for literal
code and paths whenever possible to avoid ambiguity with valid TeX commands.

Unknown code language labels fall back to plain-text highlighting with a
warning, preserving the code content.

## Markdown examples

Use standard Markdown image paths relative to the input file:

```markdown
![Results](images/results.png)
```

Write math with LaTeX syntax:

```markdown
$$
\hat{y} = X\beta
$$
```

Add a language to fenced code blocks for syntax highlighting:

````markdown
```python
print("Hello, world!")
```
````

## Troubleshooting

Check that the required commands and LaTeX package are installed:

```bash
pandoc --version
xelatex --version
latexmk --version
pygmentize -V
kpsewhich minted.sty
```

Each command should print a version or file path. If one fails, install the corresponding dependency listed above.

Overflow and missing font characters produce visible warnings while still
writing the PDF. Review those warnings: overflow may clip content, and missing
characters need a font containing those glyphs. To reject PDFs with either
problem, use strict mode (available in both converters):

```bash
ipynb2pdf analysis.ipynb --strict
md2pdf report.md --strict
```

For a failed conversion, the error includes the full log path and the retained
build directory. That directory contains `document.tex`, `pandoc.log`, and
`build.log`, plus any LaTeX logs and extracted media generated before failure.
Real TeX errors, invalid notebooks, and missing dependencies still cause
conversion to fail; arbitrary malformed input cannot always produce a valid
PDF. To inspect a successful build:

```bash
ipynb2pdf analysis.ipynb --keep-build
```

## Update

```bash
cd ~/.local/share/md2pdf
git pull
```

The `md2pdf` symlink will continue to use the updated script.

## Tests

With the conversion dependencies above, Python 3, and `pdftotext` (from
`poppler-utils`) installed, run the conversion regression tests:

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT
