"""
Generate the figures used in WRITEUP.md into docs/figures/.

Run: .venv/bin/python scripts/make_figures.py
Needs Pillow and pdftoppm (poppler-utils).
"""

import json
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO_ROOT / "images"
FIGURES_DIR = REPO_ROOT / "docs" / "figures"
PDF_PATH = REPO_ROOT / "Interview_Preparation.pdf"

FIGURE_WIDTH = 1600
ROI_PANORAMA_ID = "Kk0_Hzv4bQc2ha7esbEDcw"
# Manhole covers marked by hand on the 1600 x 400 thumbnail, for illustration only.
HAND_MARKED_COVERS = [
    (566, 376, 30),
    (302, 321, 20),
    (215, 332, 20),
    (258, 289, 15),
    (1286, 298, 16),
    (848, 268, 12),
    (1070, 264, 12),
]
# Cover examples region on page 2 of the PDF, as fractions of the page size.
COVER_EXAMPLES_BOX = (0.160, 0.188, 0.840, 0.378)


def load_metadata(json_path: Path) -> dict:
    """Load a metadata file; the sample files have a trailing comma, so strip it."""
    text = re.sub(r",\s*}", "}", json_path.read_text())
    return json.loads(text)


def load_thumbnail(panorama_id: str) -> Image.Image:
    """Load a panorama as RGB, resized to the figure width."""
    image = Image.open(IMAGES_DIR / f"{panorama_id}.png").convert("RGB")
    height = round(image.height * FIGURE_WIDTH / image.width)
    return image.resize((FIGURE_WIDTH, height), Image.LANCZOS)


def make_years_figure() -> None:
    """Stack all sample panoramas of the same location, sorted by capture date."""
    metadata = sorted(
        (load_metadata(path) for path in IMAGES_DIR.glob("*.json")),
        key=lambda item: item["date"],
    )
    font = ImageFont.load_default(size=36)
    rows = []
    for item in metadata:
        thumbnail = load_thumbnail(item["panoId"])
        draw = ImageDraw.Draw(thumbnail)
        draw.rectangle((0, 0, 170, 52), fill="black")
        draw.text((14, 6), item["date"], fill="white", font=font)
        rows.append(thumbnail)
    gap = 8
    total_height = sum(row.height for row in rows) + gap * (len(rows) - 1)
    figure = Image.new("RGB", (FIGURE_WIDTH, total_height), "white")
    top = 0
    for row in rows:
        figure.paste(row, (0, top))
        top += row.height + gap
    figure.thumbnail((1200, 10_000))
    figure.save(FIGURES_DIR / "same_location_over_years.jpg", quality=85)


def make_roi_figure() -> None:
    """Show the road region of interest and hand-marked covers on one panorama."""
    thumbnail = load_thumbnail(ROI_PANORAMA_ID)
    horizon = round(thumbnail.height * 0.52)
    overlay = Image.new("RGBA", thumbnail.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, thumbnail.width, horizon), fill=(0, 0, 0, 120))
    figure = Image.alpha_composite(thumbnail.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(figure)
    draw.line((0, horizon, thumbnail.width, horizon), fill="yellow", width=3)
    for center_x, center_y, half_size in HAND_MARKED_COVERS:
        draw.rectangle(
            (
                center_x - half_size * 1.6,
                center_y - half_size,
                center_x + half_size * 1.6,
                center_y + half_size,
            ),
            outline="red",
            width=3,
        )
    font = ImageFont.load_default(size=28)
    draw.text(
        (12, horizon - 40), "horizon: road ROI is below", fill="yellow", font=font
    )
    figure.convert("RGB").save(FIGURES_DIR / "panorama_roi.jpg", quality=85)


def make_cover_examples_figure() -> None:
    """Crop the three cover examples (sewer, water, communication) from the PDF."""
    with tempfile.TemporaryDirectory() as temporary_dir:
        prefix = Path(temporary_dir) / "page"
        subprocess.run(
            ["pdftoppm", "-f", "2", "-l", "2", "-r", "150", "-png", PDF_PATH, prefix],
            check=True,
        )
        page = Image.open(next(Path(temporary_dir).glob("page*.png"))).convert("RGB")
    left, top, right, bottom = COVER_EXAMPLES_BOX
    crop = page.crop(
        (
            round(left * page.width),
            round(top * page.height),
            round(right * page.width),
            round(bottom * page.height),
        )
    )
    crop.save(FIGURES_DIR / "cover_examples.jpg", quality=90)


def main() -> None:
    """Generate all figures."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    make_years_figure()
    make_roi_figure()
    make_cover_examples_figure()


if __name__ == "__main__":
    main()
