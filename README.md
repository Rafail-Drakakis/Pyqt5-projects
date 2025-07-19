# PyQt5 Projects

This repository contains several small desktop applications written with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/).
Each project lives in its own subdirectory and can be started directly with `python <file>.py`.

## Projects

| Directory | Description |
|-----------|-------------|
| `Calculator` | Scientific/standard calculator with toggle for advanced functions. |
| `Forex` | Simple currency exchange calculator to estimate profit or loss when rates change. |
| `Phone info` | GUI tool that analyses phone numbers (single or bulk) using the `phonenumbers` library. |
| `Presentation creator` | Builds or modifies PowerPoint presentations via `python-pptx` and JSON slide definitions. |
| `Smart notes` | Rich text note‑taking app with tagging, search and a dark/light theme. |

Output files (`*.json`, `*.txt`, `*.pptx`) are ignored by version control (see `.gitignore`).

## Requirements

- Python 3
- `PyQt5`
- Additional packages depending on the project:
  - `phonenumbers` for phone analysis
  - `python-pptx` for presentation creation

Install the required packages with `pip install PyQt5 phonenumbers python-pptx`.

## Running

Navigate into a project directory and execute the script:

```bash
cd Calculator
python calculator.py
```

Most applications run without command‑line arguments and open a GUI window.
