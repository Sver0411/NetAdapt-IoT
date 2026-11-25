# NetAdapt-IoT IEEE Journal Manuscript (`IEEEtran`)

Standalone, publication-ready 8-page IEEE double-column manuscript (`\documentclass[journal]{IEEEtran}`) covering `FUD-Ada`, 9 classical external baselines, 24 real ESP32-S3 + E220 hardware loss traces, 54-mote MIT Intel Berkeley multi-flow validation, and the zero-allocation pure C11 ESP32-S3 kernel.

## Contents

- `manuscript.tex` — Complete IEEE double-column LaTeX source (TikZ architecture diagram, 4 native `7.16 in` vector PDF figures, 4 `booktabs` tables, 17 verified BibTeX references).
- `build_figures.py` — Deterministic figure generator emitting B&W-print-safe IEEE vector PDFs (`figures/`) and Graphical Abstract directly from saved CSV/JSON outputs.
- `references.bib` — Verified peer-reviewed BibTeX entries (`IEEEtran` bibliography style).
- `manuscript.pdf` — Compiled 8-page vector PDF (`tectonic manuscript.tex`).
- `graphical_abstract.png` / `.pdf` — Mandatory IEEE Graphical Abstract.

## Rebuild Commands

```sh
python papers/netadapt-iot/build_figures.py
cd papers/netadapt-iot && tectonic manuscript.tex
```
