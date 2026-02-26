# icotool

Convert PNG or ICO images into a multi-size `.ico` file with optional rounded corners and logo scaling.

## Features

- Accepts `.png` or `.ico` input
- Generates all standard ICO sizes: **16, 32, 48, 64, 128, 256 px**
- Rounded corners with configurable radius
- Logo scaling with transparent padding
- Clean transparent backgrounds via RGBA masking

## Requirements

- Python 3.10+
- Pillow
- ImageMagick (must be available in your `PATH`)

## Usage

```
python icotool.py <input> [--radius FLOAT] [--scale FLOAT]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `input` | Source image file (`.png` or `.ico`) | — |
| `--radius` | Corner rounding as a fraction of the shortest edge (`0.0`–`0.5`) | `0.18` |
| `--scale` | Logo size relative to the canvas (`0.1`–`1.0`) | `1.0` |

### Examples

```
# Basic conversion
python icotool.py icon.png

# Custom corner radius (more rounded)
python icotool.py icon.png --radius 0.25

# Logo fills 85% of canvas (adds padding around the logo)
python icotool.py icon.png --scale 0.85

# Both options combined
python icotool.py icon.png --radius 0.20 --scale 0.90

# Convert from an existing ICO file
python icotool.py icon.ico
```

The output file is saved alongside the input with a `_output` suffix:

```
icon.png  →  icon_output.ico
```

## How It Works

1. Reads the source file and extracts the largest available frame
2. Resizes the image to 256×256 as the base
3. Optionally scales the logo within the canvas (adding transparent padding)
4. Applies rounded corners using an RGBA mask
5. Uses ImageMagick to downsample to all target sizes with Lanczos filtering
6. Combines all sizes into a single `.ico` file

## License

This project is licensed under the MIT - see the [LICENSE](LICENSE) file for details.
