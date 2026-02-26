import os
import subprocess
import argparse
from PIL import Image, ImageDraw


def round_corners(img: Image.Image, radius_pct: float = 0.18) -> Image.Image:
    """Round the corners of an image and make the background transparent."""
    img = img.convert("RGBA")
    w, h = img.size
    radius = int(min(w, h) * radius_pct)

    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)

    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    result.paste(img, mask=mask)
    return result


def scale_logo(img: Image.Image, scale: float) -> Image.Image:
    """Scale the logo within the canvas, keeping the surrounding area transparent.

    Args:
        img:   Source image.
        scale: 1.0 = fills the entire canvas; 0.8 = fills 80% (adds padding).
    """
    if scale == 1.0:
        return img

    img = img.convert("RGBA")
    w, h = img.size
    new_w = int(w * scale)
    new_h = int(h * scale)

    logo = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    offset_x = (w - new_w) // 2
    offset_y = (h - new_h) // 2
    canvas.paste(logo, (offset_x, offset_y), logo)
    return canvas


def get_largest_frame(path: str) -> Image.Image:
    """Return the largest frame from an ICO or PNG file."""
    src = Image.open(path)

    frames = []
    try:
        while True:
            frames.append((src.size, src.copy().convert("RGBA")))
            src.seek(src.tell() + 1)
    except EOFError, AttributeError:
        pass

    if not frames:
        return src.convert("RGBA")

    return sorted(frames, key=lambda x: x[0][0])[-1][1]


def convert(input_path: str, radius_pct: float = 0.18, scale: float = 1.0) -> None:
    """Convert a PNG or ICO file to a rounded, multi-size ICO.

    Args:
        input_path: Path to the source image (.png or .ico).
        radius_pct: Corner rounding as a fraction of the shortest edge (0.0–0.5).
        scale:      Logo size relative to the canvas (0.1–1.0).
    """
    base = os.path.splitext(input_path)[0]
    output_ico = base + "_output.ico"
    tmp_dir = os.path.dirname(os.path.abspath(input_path))

    print(f"[1/4] Reading source: {input_path}")
    base_img = get_largest_frame(input_path)

    base_img = base_img.resize((256, 256), Image.Resampling.LANCZOS)

    if scale != 1.0:
        print(f"[2/4] Scaling logo to {int(scale * 100)}% of canvas")
        base_img = scale_logo(base_img, scale)

    print(f"[2/4] Rounding corners (radius {int(radius_pct * 100)}%)")
    rounded_256 = round_corners(base_img, radius_pct)

    tmp_256 = os.path.join(tmp_dir, "_tmp_rounded_256.png")
    rounded_256.save(tmp_256)

    print("[3/4] Generating all sizes (16, 32, 48, 64, 128, 256)…")
    sizes = [16, 32, 48, 64, 128, 256]
    tmp_files = []

    for size in sizes:
        tmp_path = os.path.join(tmp_dir, f"_tmp_icon_{size}.png")
        subprocess.run(
            [
                "convert",
                tmp_256,
                "-resize",
                f"{size}x{size}",
                "-filter",
                "Lanczos",
                tmp_path,
            ],
            check=True,
        )
        tmp_files.append(tmp_path)

    print(f"[4/4] Building ICO: {output_ico}")
    subprocess.run(["convert"] + tmp_files + [output_ico], check=True)

    for f in tmp_files + [tmp_256]:
        os.remove(f)

    print(f"\n✓ Done: {output_ico}")

    result = subprocess.run(["identify", output_ico], capture_output=True, text=True)
    print("\nICO contents:")
    for line in result.stdout.strip().split("\n"):
        parts = line.split()
        for p in parts:
            if "x" in p and p.replace("x", "").isdigit():
                print(f"  ✓ {p}")
                break


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert PNG/ICO to a rounded, multi-size ICO file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", help="Source file (.png or .ico)")
    parser.add_argument(
        "--radius",
        type=float,
        default=0.18,
        metavar="FLOAT",
        help="Corner rounding ratio (0.0–0.5, default: 0.18)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        metavar="FLOAT",
        help="Logo size relative to canvas (0.1–1.0, default: 1.0 = full, 0.8 = 80%%)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        parser.error(f"File not found: {args.input}")

    if not (0.0 <= args.radius <= 0.5):
        parser.error("--radius must be between 0.0 and 0.5")

    if not (0.1 <= args.scale <= 1.0):
        parser.error("--scale must be between 0.1 and 1.0")

    convert(args.input, args.radius, args.scale)


if __name__ == "__main__":
    main()
