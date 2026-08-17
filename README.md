# md2pdf

Convert Markdown files to clean, submission-ready PDFs from the command line.

```bash
md2pdf report.md
```

The generated PDF supports:

- LaTeX math
- Syntax-highlighted code with automatic line wrapping
- Relative images
- Unicode text

Build files are kept in a temporary directory and removed automatically.

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
  fonts-dejavu-core
```

Pandoc 3.8 or newer is required.

### 2. Install md2pdf

```bash
git clone https://github.com/HyperCactus/markdown-to-pdf.git ~/.local/share/md2pdf
chmod +x ~/.local/share/md2pdf/md2pdf
mkdir -p ~/.local/bin
ln -sf ~/.local/share/md2pdf/md2pdf ~/.local/bin/md2pdf
```

Ensure `~/.local/bin` is on your `PATH`. Add this to `~/.bashrc` if needed:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell and check the installation:

```bash
source ~/.bashrc
md2pdf --version
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
