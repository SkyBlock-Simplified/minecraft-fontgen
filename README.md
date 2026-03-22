# Minecraft-FontGen

Convert Minecraft's bitmap font glyphs into fully functional OpenType (`.otf`) or TrueType (`.ttf`) font files.

> [!IMPORTANT]
> This tool downloads and processes **copyrighted bitmap assets owned by [Mojang AB](https://www.minecraft.net/)** (a Microsoft subsidiary) at runtime. The font textures are extracted directly from the official Minecraft client JAR and are **never distributed** with this repository. You are responsible for ensuring your use of the generated font files complies with the [Minecraft EULA](https://www.minecraft.net/en-us/eula) and [Minecraft Usage Guidelines](https://www.minecraft.net/en-us/usage-guidelines).

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Create a Virtual Environment](#create-a-virtual-environment)
  - [Install Dependencies](#install-dependencies)
- [Usage](#usage)
  - [Interactive Mode](#interactive-mode)
  - [Non-Interactive Mode](#non-interactive-mode)
  - [CLI Arguments](#cli-arguments)
  - [Environment Variables](#environment-variables)
  - [The .env File](#the-env-file)
  - [Configuration Priority](#configuration-priority)
- [Output](#output)
- [Docker Compose](#docker-compose)
  - [Basic One-Shot Task](#basic-one-shot-task)
  - [Multi-Service Example](#multi-service-example)
  - [Running the Task](#running-the-task)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Any Minecraft version** - Select any release or snapshot via the Mojang Piston API
- **OpenType (CFF) or TrueType** - Choose your preferred outline format
- **Multiple font styles** - Generate Regular, Bold, Italic, and BoldItalic variants
- **GNU Unifont fallback** - Optionally include thousands of extra Unicode glyphs from [GNU Unifont](https://unifoundry.com/unifont/) for broad script coverage
- **BMP + SMP support** - Generates cmap Format 4 (Basic Multilingual Plane) and Format 12 (Supplementary Multilingual Plane) tables
- **Pixel-perfect tracing** - Flood-fill contour tracing converts bitmap pixels into clean vector outlines
- **Debug SVG output** - Optionally dump per-glyph SVG files for visual inspection
- **Non-interactive mode** - Fully scriptable with CLI arguments and environment variables for CI/CD and Docker workflows

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| [Python](https://www.python.org/downloads/) | **3.14+** | Required |
| pip | Latest | Included with Python |
| [Git](https://git-scm.com/) | 2.x+ | For cloning the repository |

## Installation

### Clone the Repository

```bash
git clone https://github.com/SkyBlock-Simplified/minecraft-fontgen.git
cd minecraft-fontgen
```

### Create a Virtual Environment

<details>
<summary>Linux / macOS</summary>

```bash
python3.14 -m venv .venv
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

### Install Dependencies

Install in **editable mode** (recommended for development):

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode

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

### Non-Interactive Mode

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

### CLI Arguments

All arguments are optional. When omitted, values fall back to environment
variables, then to `.env` file values, then to built-in defaults.

| Argument | Description | Default |
|----------|-------------|---------|
| `--version <version>` | Minecraft version to compile (skips interactive prompt) | Interactive prompt |
| `--output <path>` | Directory for generated font files | `output` |
| `--styles <list>` | Comma-separated font styles to generate | `regular,bold,italic,bolditalic` |
| `--silent` | Suppress all output except errors | Disabled |

**Styles** accepts any combination of: `regular`, `bold`, `italic`, `bolditalic`.

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
| `FONTGEN_SILENT` | Suppress output (`1`, `true`, or `yes`) | `--silent` | `true` |

```bash
export FONTGEN_VERSION=1.21.4
export FONTGEN_STYLES=regular,bold
export FONTGEN_SILENT=true
python -m minecraft_fontgen
```

### The .env File

You can create a `.env` file in the project root to set defaults without
modifying your shell environment. The file is loaded automatically at startup.

```dotenv
# .env
FONTGEN_VERSION=1.21.4
FONTGEN_OUTPUT=output
FONTGEN_STYLES=regular,bold,italic,bolditalic
FONTGEN_SILENT=false
```

Values from `.env` will **not** overwrite variables that already exist in your
shell environment.

### Configuration Priority

Values are resolved in this order (highest priority first):

```
CLI argument  >  Shell environment variable  >  .env file  >  config.py defaults
```

For example, if `FONTGEN_OUTPUT=dist` is in your `.env` but you run
`python -m minecraft_fontgen --output build`, the output directory will be
`build`.

## Output

Generated font files are written to the output directory (default: `output/`):

```
output/
├── Minecraft-Regular.otf
├── Minecraft-Bold.otf
├── Minecraft-Italic.otf
└── Minecraft-BoldItalic.otf
```

The file extension is `.otf` for OpenType (CFF) or `.ttf` for TrueType,
controlled by the `OPENTYPE` constant in
[`config.py`](src/minecraft_fontgen/config.py).

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
    image: python:3.14-slim
    working_dir: /build
    environment:
      FONTGEN_VERSION: "1.21.4"
      FONTGEN_STYLES: "regular,bold"
      FONTGEN_SILENT: "true"
      FONTGEN_OUTPUT: "/output"
    volumes:
      - fonts:/output
    entrypoint: ["bash", "-c"]
    command:
      - |
        pip install --quiet git+https://github.com/SkyBlock-Simplified/minecraft-fontgen.git &&
        minecraft-fontgen
    profiles:
      - build

volumes:
  fonts:
```

> [!TIP]
> The `profiles: [build]` setting prevents this service from starting during a
> normal `docker compose up`. It only runs when explicitly invoked.

### Multi-Service Example

Here's a more complete example where a Discord bot service depends on the
generated fonts:

```yaml
services:
  fontgen:
    image: python:3.14-slim
    working_dir: /build
    environment:
      FONTGEN_VERSION: "1.21.4"
      FONTGEN_STYLES: "regular,bold"
      FONTGEN_SILENT: "true"
      FONTGEN_OUTPUT: "/output"
    volumes:
      - fonts:/output
    entrypoint: ["bash", "-c"]
    command:
      - |
        pip install --quiet git+https://github.com/SkyBlock-Simplified/minecraft-fontgen.git &&
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

The tool runs a five-stage pipeline:

```
1. Clean       Wipes and recreates work/ and output/ directories
       ↓
2. Download    Fetches the Minecraft version manifest from the Piston API,
               downloads the client JAR, extracts font assets, and optionally
               downloads GNU Unifont hex files
       ↓
3. Parse       Reads font provider JSON from the extracted JAR, discovers
               bitmap PNG textures and Unicode character mappings, then slices
               individual glyphs from the bitmap sheets using flood-fill
               contour tracing
       ↓
4. Build       Merges provider glyphs (high priority) with unifont fallback
               glyphs (low priority) into a unified glyph map, keyed by
               codepoint and grouped by style. Pre-computes scaled coordinates
               (pixel space → font units) for all glyphs
       ↓
5. Create      Initializes fontTools TTFont tables for each enabled style,
               converts all glyphs with a single progress bar, applies italic
               shear transforms where needed, then finalizes and saves the
               font files
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
├── src/minecraft_fontgen/
│   ├── __init__.py
│   ├── __main__.py          # python -m entry point
│   ├── main.py              # Pipeline orchestration
│   ├── cli.py               # Argument parsing, env var resolution
│   ├── config.py            # Constants and runtime configuration
│   ├── piston.py            # Mojang Piston API, JAR/unifont downloads
│   ├── file_io.py           # Bitmap slicing, contour tracing, glyph maps
│   ├── font_creator.py      # Batch font file creation
│   ├── functions.py         # Shared utilities (logging, HTTP, codepoints)
│   ├── glyph/
│   │   ├── glyph.py         # Glyph scaling, transforms, pen drawing
│   │   └── glyph_storage.py # Glyph accumulation, cmap, final output
│   └── table/               # One file per OpenType/TrueType table
│       ├── header.py         # head
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
├── requirements.txt
├── LICENSE
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
