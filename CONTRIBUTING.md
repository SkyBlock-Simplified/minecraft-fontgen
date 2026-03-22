# Contributing to Minecraft-FontGen

Thank you for your interest in contributing! This document explains how to get
started, what to expect during the review process, and the conventions this
project follows.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Development Setup](#development-setup)
- [Making Changes](#making-changes)
  - [Branching Strategy](#branching-strategy)
  - [Code Style](#code-style)
  - [Commit Messages](#commit-messages)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Issues](#reporting-issues)
- [Project Architecture](#project-architecture)
- [Legal](#legal)

## Getting Started

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.14+ | Required for the `t-string` and other modern features used |
| pip | Latest | Comes with Python |
| Git | 2.x+ | For cloning and contributing |

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/SkyBlock-Simplified/minecraft-fontgen.git
   cd minecraft-fontgen
   ```

2. **Create and activate a virtual environment**

   ```bash
   # Linux / macOS
   python3.14 -m venv .venv
   source .venv/bin/activate

   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install in editable mode**

   This installs the package and all dependencies so that changes to the source
   files are reflected immediately without reinstalling.

   ```bash
   pip install -e .
   ```

4. **Verify the installation**

   ```bash
   python -m minecraft_fontgen --help
   ```

## Making Changes

### Branching Strategy

- Create a feature branch from `master` for your work.
- Use a descriptive branch name: `fix/cmap-format12-overflow`, `feat/svg-export`,
  `docs/docker-instructions`.

```bash
git checkout -b feat/my-feature master
```

### Code Style

This project does not currently enforce a linter or formatter, but please follow
these conventions:

- **Imports** - Use absolute imports from the `minecraft_fontgen` package.
  ```python
  from minecraft_fontgen.config import UNITS_PER_EM
  ```
- **Naming** - `snake_case` for functions and variables, `UPPER_SNAKE_CASE` for
  module-level constants, `PascalCase` for classes.
- **Docstrings** - Every public function should have a one-line docstring
  describing what it does.
- **Type hints** - Encouraged but not strictly required. Use them where they
  clarify intent.
- **Line length** - Aim for 120 characters or less.

### Commit Messages

Write clear, concise commit messages that describe *what* changed and *why*.

```
Add FONTGEN_VERSION env var for non-interactive version selection

Allows CI/CD and Docker workflows to specify the Minecraft version
without requiring an interactive terminal prompt.
```

- Use the imperative mood ("Add", "Fix", "Update", not "Added", "Fixes").
- Keep the subject line under 72 characters.
- Add a body when the *why* isn't obvious from the subject.

## Submitting a Pull Request

1. **Push your branch** to your fork.

   ```bash
   git push origin feat/my-feature
   ```

2. **Open a Pull Request** against the `master` branch of
   [SkyBlock-Simplified/minecraft-fontgen](https://github.com/SkyBlock-Simplified/minecraft-fontgen).

3. **In the PR description**, include:
   - A summary of the changes and the motivation behind them.
   - Steps to test or verify the changes (e.g., specific Minecraft versions,
     CLI flags, expected output).
   - Screenshots of generated font output if relevant (glyph rendering, debug
     SVGs, etc.).

4. **Respond to review feedback.** PRs may go through one or more rounds of
   review before being merged.

### What gets reviewed

- Correctness of glyph processing and font table output.
- Whether new configuration options follow the existing priority chain
  (CLI arg > env var > `.env` file > `config.py` defaults).
- Impact on the generated font files (any change to glyph tracing, scaling,
  or table construction should be verified with a font validator like
  FontForge or `fontTools.ttLib`).

## Reporting Issues

Use [GitHub Issues](https://github.com/SkyBlock-Simplified/minecraft-fontgen/issues)
to report bugs or request features.

When reporting a bug, include:

- **Python version** (`python --version`)
- **Operating system**
- **Minecraft version** you targeted
- **Full error traceback** (if applicable)
- **Steps to reproduce**
- **Expected vs. actual behavior**

## Project Architecture

A brief overview to help you find your way around the codebase:

```
src/minecraft_fontgen/
├── main.py             # Pipeline entry point (clean → download → parse → build → create)
├── cli.py              # Argument parsing and env var resolution
├── config.py           # All constants and runtime configuration
├── piston.py           # Mojang Piston API interaction, JAR/unifont downloading
├── file_io.py          # Bitmap slicing, contour tracing, glyph map building
├── font_creator.py     # Batch font file creation across all styles
├── functions.py        # Shared utilities (logging, HTTP, codepoint helpers)
├── glyph/
│   ├── glyph.py        # Single glyph: scaling, shear transforms, pen drawing
│   └── glyph_storage.py# Glyph accumulation, cmap management, final write
└── table/
    ├── header.py       # head table
    ├── horizontal_header.py  # hhea table
    ├── horizontal_metrics.py # hmtx table
    ├── maximum_profile.py    # maxp table
    ├── postscript.py         # post table
    ├── name.py               # name table
    ├── os2_metrics.py        # OS/2 table
    ├── glyph_mappings.py     # cmap table (Format 4 + Format 12)
    ├── opentype.py           # CFF tables
    └── truetype.py           # glyf/loca tables
```

### Pipeline flow

```
parse_args() → clean_directories() → read_minecraft_piston_api()
  → read_providers_from_file() → build_glyph_map() → create_font_files()
```

If your change touches glyph processing (`file_io.py`, `glyph/`), test with
both OpenType (`OPENTYPE = True`) and TrueType (`OPENTYPE = False`) output.
If it touches table construction (`table/`), validate the output with FontForge.

## Legal

By submitting a pull request, you agree that your contributions are licensed
under the [Apache License 2.0](LICENSE.md), the same license that covers this
project.

This project processes copyrighted assets owned by Mojang AB at runtime. Do not
commit any Minecraft assets (textures, JARs, JSON files extracted from the
client) to the repository.
