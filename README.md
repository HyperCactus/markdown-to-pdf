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

Build files are kept in a temporary directory and removed automatically.
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

LaTeX environments in Markdown cells (such as `align` and `align*`) are
supported. When a cell output contains multiple MIME representations, the
richest supported representation is used, so saved plots render as figures
instead of their plain-text descriptions.

Unicode mathematical characters in code cells are rendered automatically
using Noto Sans Math as a fallback font.

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

## Update

```bash
cd ~/.local/share/md2pdf
git pull
```

The `md2pdf` symlink will continue to use the updated script.

## License

MIT
