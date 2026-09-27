"""Build an editable PowerPoint container from the deck's reviewed slide renders.

Each slide is a full-bleed rendered image so the PDF and PPTX have identical layout.
Run generate_deck.py first.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".build" / "python-pptx"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

from pptx import Presentation
from pptx.util import Inches

slides_dir = HERE / "rendered"
output = HERE / "ClearSpend_Pitch_Deck.pptx"
paths = sorted(slides_dir.glob("[0-9][0-9].png"))
if len(paths) != 11:
    raise SystemExit("Expected 11 rendered slide PNGs. Run generate_deck.py first.")

presentation = Presentation()
presentation.slide_width = Inches(13.333333)
presentation.slide_height = Inches(7.5)
blank = presentation.slide_layouts[6]

for image_path in paths:
    slide = presentation.slides.add_slide(blank)
    slide.shapes.add_picture(
        str(image_path), 0, 0,
        width=presentation.slide_width,
        height=presentation.slide_height,
    )

# The default empty slide is not part of presentation.slides until added; all slides above are intentional.
presentation.save(output)
print(f"Created {output}")
