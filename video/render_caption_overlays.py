#!/usr/bin/env python3
"""Render the project's SRT captions as transparent full-frame PNG overlays."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1920, 1080
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"


def seconds(value: str) -> float:
    hours, minutes, tail = value.split(":")
    secs, millis = tail.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(secs) + int(millis) / 1000


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: render_caption_overlays.py CAPTIONS.srt OUTPUT_DIR", file=sys.stderr)
        return 2
    source, output = Path(sys.argv[1]), Path(sys.argv[2])
    output.mkdir(parents=True, exist_ok=True)
    blocks = re.split(r"\n\s*\n", source.read_text(encoding="utf-8").strip())
    font = ImageFont.truetype(FONT, 42)
    concat_lines = ["ffconcat version 1.0"]
    for index, block in enumerate(blocks, 1):
        lines = block.splitlines()
        start, end = (part.strip() for part in lines[1].split("-->", 1))
        text = "\n".join(lines[2:])
        image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        box = draw.multiline_textbbox((0, 0), text, font=font, spacing=10, align="center", stroke_width=1)
        text_width, text_height = box[2] - box[0], box[3] - box[1]
        x, y = (WIDTH - text_width) / 2, HEIGHT - text_height - 58
        draw.rounded_rectangle((x - 28, y - 20, x + text_width + 28, y + text_height + 22), radius=16, fill=(8, 18, 13, 205))
        draw.multiline_text((x, y), text, font=font, fill="white", spacing=10, align="center", stroke_width=1, stroke_fill=(0, 0, 0, 180))
        path = output / f"caption_{index:02d}.png"
        image.save(path)
        concat_lines.extend((f"file '{path}'", f"duration {seconds(end) - seconds(start):.3f}"))
    concat_lines.append(f"file '{output / f'caption_{len(blocks):02d}.png'}'")
    (output / "captions.ffconcat").write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
