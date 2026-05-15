# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build commands

All build output goes to the `build/` directory. The project uses **XeLaTeX** (not pdflatex) because it relies on `fontspec` and `polyglossia`.

Full build with bibliography (required after adding/changing references):
```bash
xelatex -synctex=1 -interaction=nonstopmode -file-line-error -shell-escape -output-directory=build main.tex
biber build/main
xelatex -synctex=1 -interaction=nonstopmode -file-line-error -shell-escape -output-directory=build main.tex
xelatex -synctex=1 -interaction=nonstopmode -file-line-error -shell-escape -output-directory=build main.tex
```

Quick build (content changes only, no bibliography changes):
```bash
xelatex -synctex=1 -interaction=nonstopmode -file-line-error -shell-escape -output-directory=build main.tex
xelatex -synctex=1 -interaction=nonstopmode -file-line-error -shell-escape -output-directory=build main.tex
```

## Architecture

```
main.tex          — entry point; loads config, macros, all packages, stitches pages and chapters
config.tex        — all document parameters and feature flags (edit this to change metadata/features)
macros.tex        — custom LaTeX commands
references.bib    — BibTeX bibliography (GOST-numeric style via biblatex + biber)
chapters/         — one file per chapter, included via \input in main.tex
pages/            — titlepage.tex, bibliography.tex (structural pages, not content)
images/           — raster images; \graphicspath includes this and figures/
figures/          — vector/generated figures (empty by default, kept via .gitkeep)
build/            — all compiler output (gitignored)
```

## Feature flags in config.tex

Optional packages are guarded by boolean flags at the top of `config.tex`. Toggle them before adding the corresponding LaTeX:

| Flag | Default | Enables |
|------|---------|---------|
| `\ifbib` / `\bibtrue` | on | `biblatex` + biber (GOST bibliography) |
| `\ifplots` / `\plotsfalse` | off | `pgfplots` |
| `\iftikz` / `\tikzfalse` | off | `tikz` + geometry/arrow libraries |
| `\iflisting` / `\listingfalse` | off | `minted` (requires `-shell-escape`) |

## Custom commands (macros.tex)

| Command | Purpose |
|---------|---------|
| `\unnsection{title}` | Unnumbered section that still appears in the ToC |
| `\unnsubsection{title}` | Same for subsection level |
| `\unnsubsubsection{title}` | Same for subsubsection level |

## Document metadata

All student/course data lives exclusively in `config.tex`: `\lastName`, `\firstName`, `\middleName`, `\group`, `\discipline`, `\topic`, `\supervisor`, `\kafedraFirstString`, `\kafedraSecondString`, `\specialization`, `\trainingProfile`, `\yearFooter`. Never hardcode these in chapter or page files.

## Language

Primary language is Russian (`\setdefaultlanguage{russian}` via polyglossia). Other configured languages: English, German, French. On Linux, fonts default to Liberation Serif / Liberation Mono; on macOS to Times New Roman / Courier New — this is handled automatically by `ifplatform` in `config.tex`.
