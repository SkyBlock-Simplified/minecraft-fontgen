# Minecraft-FontGen

Convert Minecraft's bitmap font glyphs into fully functional OpenType (`.otf`) or TrueType (`.ttf`) font files.

> [!IMPORTANT]
> This tool downloads and processes **copyrighted bitmap assets owned by [Mojang AB](https://www.minecraft.net/)** (a Microsoft subsidiary) at runtime. The font textures are extracted directly from the official Minecraft client JAR and are **never distributed** with this repository. You are responsible for ensuring your use of the generated font files complies with the [Minecraft EULA](https://www.minecraft.net/en-us/eula) and [Minecraft Usage Guidelines](https://www.minecraft.net/en-us/usage-guidelines).

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
  - [IntelliJ IDEA](#intellij-idea)
  - [CLI Arguments](#cli-arguments)
  - [Environment Variables](#environment-variables)
- [Output](#output)
- [Unicode Coverage](#unicode-coverage)
- [Docker Compose](#docker-compose)
  - [Basic One-Shot Task](#basic-one-shot-task)
  - [Running the Task](#running-the-task)
- [How It Works](#how-it-works)
  - [Glyph Processing](#glyph-processing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Any Minecraft version** - Select any release or snapshot via the Mojang Piston API
- **OpenType (CFF) or TrueType** - Choose your preferred outline format
- **Multiple font styles** - Generate Regular, Bold, Italic, BoldItalic, plus alternate scripts (Galactic, Illageralt) on supported versions
- **GNU Unifont fallback** - Optionally include thousands of extra Unicode glyphs from [GNU Unifont](https://unifoundry.com/unifont/) for broad script coverage
- **BMP + SMP support** - Generates cmap Format 4 (Basic Multilingual Plane) and Format 12 (Supplementary Multilingual Plane) tables
- **Pixel-perfect tracing** - Flood-fill contour tracing converts bitmap pixels into clean vector outlines
- **Debug SVG output** - Optionally dump per-glyph SVG files for visual inspection
- **Non-interactive mode** - Fully scriptable with CLI arguments and environment variables for CI/CD and Docker workflows

## Getting Started

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| [Python](https://www.python.org/downloads/) | **3.10+** | Required |
| pip | Latest | Included with Python |
| [Git](https://git-scm.com/) | 2.x+ | For cloning the repository |

### Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/SkyBlock-Simplified/minecraft-fontgen.git
cd minecraft-fontgen
```

<details>
<summary>Linux / macOS</summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
```

</details>

<details>
<summary>Windows</summary>

```powershell
python -m venv .venv
.venv\Scripts\activate
```

</details>

Install the package and its dependencies:

```bash
pip install -e .
```

### Usage

#### Interactive Mode

When no `--version` flag or `FONTGEN_VERSION` env var is set, the tool launches
an interactive prompt where you can search and select a Minecraft version:

```bash
python -m minecraft_fontgen
```

The interactive prompt supports the following commands:

| Command | Description |
|---------|-------------|
| `<version>` | Enter a version number directly (e.g., `1.21.4`) |
| `r` or `releases` | List all available release versions |
| `s` or `snapshots` | List all available snapshot versions |
| `h`, `?`, or `help` | Show help |
| `exit` or `quit` | Exit the tool |

#### Non-Interactive Mode

For automation, CI/CD pipelines, or Docker, provide the Minecraft version
upfront to skip the interactive prompt entirely:

```bash
# Via CLI argument
python -m minecraft_fontgen --version 1.21.4

# Via environment variable
FONTGEN_VERSION=1.21.4 python -m minecraft_fontgen

# Combine multiple options
python -m minecraft_fontgen --version 1.21.4 --styles regular,bold --output dist/fonts --silent
```

### IntelliJ IDEA

The repository includes a shared run configuration for
[IntelliJ IDEA](https://www.jetbrains.com/idea/) and
[PyCharm](https://www.jetbrains.com/pycharm/). After opening the project, the
**main** configuration appears automatically in the **Run/Debug** toolbar.

To run or debug:

1. Open the project in IntelliJ IDEA or PyCharm.
2. Select **main** from the run configuration dropdown in the toolbar.
3. Click **Run** (▶) or **Debug** (🪲) to start the tool.

The configuration runs `python -m minecraft_fontgen` using the project's
Python virtual environment with these environment variables pre-set:

| Variable | Value | Purpose |
|----------|-------|---------|
| `FONTGEN_VALIDATE` | `1` | Runs FontForge validation after build |
| `PYTHONUNBUFFERED` | `1` | Ensures real-time console output |

To pass additional arguments (e.g. `--version 1.21.4`), open the configuration
editor (**Run > Edit Configurations**) and add them to the **Parameters** field.
You can also add or override environment variables in the **Environment
variables** section of the same dialog.

### CLI Arguments

All arguments are optional. When omitted, values fall back to environment
variables, then to `.env` file values, then to built-in defaults.

| Argument | Description | Default |
|----------|-------------|---------|
| `--version <version>` | Minecraft version to compile (skips interactive prompt) | Interactive prompt |
| `--output <path>` | Directory for generated font files | `output` |
| `--styles <list>` | Comma-separated font styles to generate | All enabled in `config.py` |
| `--type <type>` | Font type: `opentype`/`otf` or `truetype`/`ttf` | `opentype` |
| `--silent` | Suppress all output except errors | Disabled |
| `--validate` | Run FontForge validation after build (requires `fontforge`) | Disabled |

**Styles** accepts any combination of: `regular`, `bold`, `italic`, `bolditalic`, `galactic`, `illageralt`.

```bash
# Only generate Regular and Bold
python -m minecraft_fontgen --styles regular,bold

# Custom output directory
python -m minecraft_fontgen --output build/fonts

# Silent mode for scripts
python -m minecraft_fontgen --silent --version 1.21.4
```

> [!NOTE]
> The `--styles` flag controls which style variants are generated. BoldItalic
> is only produced when both `bold` and `italic` are present *or* `bolditalic`
> is explicitly listed.

### Environment Variables

Every CLI argument has a corresponding environment variable. These are useful
for Docker, CI/CD, or when you want to set defaults without passing flags
every time.

| Variable | Description | Equivalent CLI | Example |
|----------|-------------|----------------|---------|
| `FONTGEN_VERSION` | Minecraft version to compile | `--version` | `1.21.4` |
| `FONTGEN_OUTPUT` | Output directory path | `--output` | `dist/fonts` |
| `FONTGEN_STYLES` | Comma-separated font styles | `--styles` | `regular,bold` |
| `FONTGEN_TYPE` | Font type: `opentype`/`otf` or `truetype`/`ttf` | `--type` | `opentype` |
| `FONTGEN_SILENT` | Suppress output (`1`, `true`, or `yes`) | `--silent` | `true` |
| `FONTGEN_VALIDATE` | Run FontForge validation after build (`1`, `true`, or `yes`) | `--validate` | `false` |

```bash
export FONTGEN_VERSION=1.21.4
export FONTGEN_STYLES=regular,bold
export FONTGEN_SILENT=true
python -m minecraft_fontgen
```

<details>
<summary>The <code>.env</code> file and configuration priority</summary>

You can create a `.env` file in the project root to set defaults without
modifying your shell environment. The file is loaded automatically at startup.

```dotenv
# .env
FONTGEN_VERSION=1.21.4
FONTGEN_OUTPUT=output
FONTGEN_STYLES=regular,bold,italic,bolditalic,galactic,illageralt
FONTGEN_TYPE=opentype
FONTGEN_SILENT=false
FONTGEN_VALIDATE=false
```

Values from `.env` will **not** overwrite variables that already exist in your
shell environment.

Configuration values are resolved in this order (highest priority first):

```
CLI argument  >  Shell environment variable  >  .env file  >  config.py defaults
```

For example, if `FONTGEN_OUTPUT=dist` is in your `.env` but you run
`python -m minecraft_fontgen --output build`, the output directory will be
`build`.

</details>

## Output

Generated font files are written to the output directory (default: `output/`):

```
output/
├── Minecraft-Regular.otf
├── Minecraft-Bold.otf
├── Minecraft-Italic.otf
├── Minecraft-BoldItalic.otf
├── Minecraft-Galactic.otf      # Minecraft 1.13+ only
└── Minecraft-Illageralt.otf    # Minecraft 1.13+ only
```

> [!NOTE]
> Galactic (Standard Galactic Alphabet) and Illageralt
> (Illager Runic Script) are only available on Minecraft versions that include their
> font provider JSON files (1.13+). On older versions these styles are
> automatically skipped.

The file extension is `.otf` for OpenType (CFF) or `.ttf` for TrueType,
controlled by `--type` / `FONTGEN_TYPE` (or the `OPENTYPE` constant in
[`config.py`](minecraft_fontgen/config.py)).

## Unicode Coverage

The generated fonts include glyphs from Minecraft's bitmap providers and
optionally from [GNU Unifont](https://unifoundry.com/unifont/) as a fallback.

> [!NOTE]
> Provider glyphs from Minecraft's bitmap PNGs are always included regardless
> of the ranges below. These ranges control which additional glyphs are pulled
> from GNU Unifont (1.13+) and which codepoints are included from
> `glyph_sizes.bin` (1.12.2 and earlier). To customize coverage, edit
> `UNIFONT_RANGES` in [`config.py`](minecraft_fontgen/config.py).

<details>
<summary>Unicode block coverage (<code>UNIFONT_RANGES</code>)</summary>

| Unicode Block | Range | Status |
|---------------|-------|--------|
| Basic Latin | U+0000–U+007F | ✅ Included |
| Latin-1 Supplement | U+0080–U+00FF | ✅ Included |
| Latin Extended-A/B | U+0100–U+024F | ✅ Included |
| IPA Extensions | U+0250–U+02AF | ✅ Included |
| Spacing Modifier Letters | U+02B0–U+02FF | ✅ Included |
| Combining Diacritical Marks | U+0300–U+036F | ✅ Included |
| Greek and Coptic | U+0370–U+03FF | ✅ Included |
| Cyrillic / Supplement | U+0400–U+052F | ✅ Included |
| Armenian | U+0530–U+058F | ✅ Included |
| Hebrew | U+0590–U+05FF | ✅ Included |
| Arabic / Supplement | U+0600–U+077F | ✅ Included |
| Syriac | U+0700–U+074F | ✅ Included |
| Thaana | U+0780–U+07BF | ✅ Included |
| NKo | U+07C0–U+07FF | ✅ Included |
| Devanagari | U+0900–U+097F | ❌ Excluded |
| Bengali / Gurmukhi / Gujarati | U+0980–U+0AFF | ❌ Excluded |
| Tamil / Telugu / Kannada / Malayalam | U+0B00–U+0D7F | ❌ Excluded |
| Sinhala | U+0D80–U+0DFF | ❌ Excluded |
| Thai | U+0E00–U+0E7F | ✅ Included |
| Lao / Tibetan / Myanmar | U+0E80–U+109F | ❌ Excluded |
| Georgian | U+10A0–U+10FF | ✅ Included |
| Hangul Jamo | U+1100–U+11FF | ✅ Included |
| Ethiopic | U+1200–U+137F | ❌ Excluded |
| Cherokee / Unified Canadian Aboriginal | U+13A0–U+167F | ❌ Excluded |
| Ogham / Runic | U+1680–U+16FF | ❌ Excluded |
| Khmer / Mongolian | U+1780–U+18AF | ❌ Excluded |
| Phonetic Extensions + Supplement | U+1D00–U+1DFF | ✅ Included |
| Latin Extended Additional | U+1E00–U+1EFF | ✅ Included |
| Greek Extended | U+1F00–U+1FFF | ✅ Included |
| General Punctuation through Misc Symbols | U+2000–U+2BFF | ✅ Included |
| Glagolitic / Latin Extended-C | U+2C00–U+2C7F | ✅ Included |
| Coptic | U+2C80–U+2CFF | ✅ Included |
| Supplemental Punctuation | U+2E00–U+2E7F | ✅ Included |
| CJK Radicals / Kangxi / Ideographs | U+2E80–U+9FFF | ❌ Excluded |
| Yi Syllables / Radicals | U+A000–U+A4CF | ❌ Excluded |
| Latin Extended-D | U+A720–U+A7FF | ✅ Included |
| Latin Extended-E | U+AB30–U+AB6F | ✅ Included |
| Hangul Syllables | U+AC00–U+D7AF | ❌ Excluded |
| Surrogates / Private Use Area | U+D800–U+F8FF | ❌ Excluded |
| CJK Compatibility Ideographs | U+F900–U+FAFF | ❌ Excluded |
| Latin Ligatures (Alphabetic Presentation) | U+FB00–U+FB06 | ✅ Included |
| Arabic Presentation Forms-A/B | U+FB50–U+FDFB | ❌ Excluded |
| Combining Half Marks | U+FE20–U+FE2F | ✅ Included |
| Small Form Variants | U+FE50–U+FE6F | ✅ Included |
| Fullwidth ASCII | U+FF01–U+FF5E | ✅ Included |
| Specials | U+FFF0–U+FFFD | ✅ Included |

</details>

## Docker Compose

Minecraft-FontGen can be used as a **one-shot build task** in a Docker Compose
stack. This is useful when another service (a Discord bot, a web app, a resource
pack compiler, etc.) needs the generated font files but you don't want to host
them in a repository or keep a persistent container running.

The pattern:
1. An ephemeral container clones the repo, installs the tool, and compiles the fonts.
2. The output is written to a shared volume.
3. The container exits and is removed automatically.
4. Other services mount the same volume to consume the font files.

### Basic One-Shot Task

Add this service to your project's `docker-compose.yml`:

```yaml
services:
  fontgen:
    image: python:3-slim
    user: "1000:1000"
    working_dir: /build
    environment:
      FONTGEN_VERSION: "1.21.4"
      FONTGEN_STYLES: "regular,bold"
      FONTGEN_SILENT: "true"
      FONTGEN_OUTPUT: "/output"
      PATH: "/home/fontgen/.local/bin:$PATH"
    volumes:
      - fonts:/output
    entrypoint: ["bash", "-c"]
    command:
      - |
        pip install --user --quiet git+https://github.com/SkyBlock-Simplified/minecraft-fontgen.git &&
        minecraft-fontgen
    profiles:
      - build

volumes:
  fonts:
```

> [!TIP]
> The `profiles: [build]` setting prevents this service from starting during a
> normal `docker compose up`. It only runs when explicitly invoked.

<details>
<summary>Multi-service example (bot depends on font generation)</summary>

```yaml
services:
  fontgen:
    image: python:3-slim
    user: "1000:1000"
    working_dir: /build
    environment:
      FONTGEN_VERSION: "1.21.4"
      FONTGEN_STYLES: "regular,bold"
      FONTGEN_SILENT: "true"
      FONTGEN_OUTPUT: "/output"
      PATH: "/home/fontgen/.local/bin:$PATH"
    volumes:
      - fonts:/output
    entrypoint: ["bash", "-c"]
    command:
      - |
        pip install --user --quiet git+https://github.com/SkyBlock-Simplified/minecraft-fontgen.git &&
        minecraft-fontgen

  bot:
    build: .
    volumes:
      - fonts:/app/fonts:ro
    depends_on:
      fontgen:
        condition: service_completed_successfully
    environment:
      FONT_PATH: /app/fonts

volumes:
  fonts:
```

In this setup:
- `fontgen` runs first, compiles the fonts into the shared `fonts` volume, then exits.
- `bot` waits for `fontgen` to complete successfully before starting.
- The `bot` service mounts the same volume as read-only (`:ro`) at `/app/fonts`.

</details>

### Running the Task

```bash
# Run only the font generation task
docker compose run --rm fontgen

# Or if using profiles
docker compose --profile build run --rm fontgen

# Start the full stack (bot waits for fontgen to finish)
docker compose up
```

> [!NOTE]
> The `--rm` flag automatically removes the container after it exits, so no
> cleanup is needed.

To **rebuild fonts** (e.g., after a Minecraft version update), remove the
existing volume and re-run:

```bash
docker volume rm <project>_fonts
docker compose run --rm fontgen
```

## How It Works

The tool runs a six-stage pipeline:

```
1. Clean       Wipes and recreates work/ and output/ directories
       ↓
2. Download    Fetches the Minecraft version manifest from the Piston API,
               downloads the client JAR, extracts font assets, and optionally
               downloads GNU Unifont hex files
       ↓
3. Parse       Detects the font asset format and parses accordingly:
               - JSON (1.13+): Reads default.json font providers with
                 explicit Unicode character mappings
               - Binary (1.12.2 and earlier): Reads glyph_sizes.bin
                 width data and unicode_page_XX.png / ascii.png textures
               Slices individual glyphs from the bitmap sheets using
               flood-fill contour tracing
       ↓
4. Build       Merges provider glyphs (high priority) with unifont fallback
               glyphs (low priority) into a unified glyph map, keyed by
               codepoint and grouped by style. Processes alternate fonts
               (Galactic, Illageralt) by overlaying their glyphs onto the
               Regular map. Pre-computes scaled coordinates (pixel space →
               font units) for all glyphs
       ↓
5. Create      Initializes fontTools TTFont tables for each enabled style,
               converts all glyphs with a single progress bar, applies italic
               shear transforms where needed, then finalizes and saves the
               font files
       ↓
6. Validate    (Optional, --validate) Runs FontForge validation on all
               generated font files, reporting per-glyph errors by type
```

### Glyph Processing

Each bitmap glyph goes through:

1. **Flood-fill labeling** - Identifies connected pixel groups
2. **Boundary tracing** - Right-hand rule extracts contour edges
3. **Corner extraction** - Converts edges to corner points for vector outlines
4. **Bold expansion** - Bold glyphs get a 1px rightward expansion before tracing
5. **Coordinate scaling** - Pixel coordinates are mapped to font units (`UNITS_PER_EM = 1024`)
6. **Italic shear** - Italic variants apply a shear transform to the pre-computed coordinates
7. **Pen drawing** - `T2CharStringPen` for CFF outlines or `TTGlyphPen` for TrueType

## Project Structure

```
minecraft-fontgen/
├── minecraft_fontgen/
│   ├── __init__.py
│   ├── __main__.py                # python -m entry point
│   ├── main.py                    # Pipeline orchestration
│   ├── cli.py                     # Argument parsing, env var resolution
│   ├── config.py                  # Constants and runtime configuration
│   ├── piston.py                  # Mojang Piston API, JAR/unifont downloads
│   ├── file_io.py                 # Bitmap slicing, contour tracing, glyph maps
│   ├── font_creator.py            # Batch font file creation
│   ├── functions.py               # Shared utilities (logging, HTTP, codepoints)
│   ├── validate_font.py           # FontForge validation script (--validate)
│   ├── glyph/
│   │   ├── glyph.py               # Glyph scaling, transforms, pen drawing
│   │   └── glyph_storage.py       # Glyph accumulation, cmap, final output
│   └── table/                     # One file per OpenType/TrueType table
│       ├── header.py              # head
│       ├── horizontal_header.py   # hhea
│       ├── horizontal_metrics.py  # hmtx
│       ├── maximum_profile.py     # maxp
│       ├── postscript.py          # post
│       ├── name.py                # name
│       ├── os2_metrics.py         # OS/2
│       ├── glyph_mappings.py      # cmap (Format 4 + 12)
│       ├── opentype.py            # CFF tables
│       └── truetype.py            # glyf/loca tables
├── pyproject.toml
├── LICENSE.md
├── COPYRIGHT.md
├── CONTRIBUTING.md
└── CLAUDE.md
```

### Runtime Directories

These are created during execution and excluded from version control:

| Directory | Contents |
|-----------|----------|
| `work/` | Downloaded JAR, extracted assets, sliced tile bitmaps, debug SVGs |
| `output/` | Generated `.otf` or `.ttf` font files |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style
guidelines, and how to submit a pull request.

## License

This project is licensed under the **Apache License 2.0** - see [LICENSE](LICENSE.md)
for the full text.

See [COPYRIGHT.md](COPYRIGHT.md) for third-party attribution notices, including
information about Mojang AB's copyrighted assets and GNU Unifont licensing.
