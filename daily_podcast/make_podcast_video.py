#!/usr/bin/env python3
import argparse
from pathlib import Path

from moviepy import AudioFileClip, ImageClip
from PIL import Image, ImageDraw, ImageFont


def _load_font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int):
    tokens = text.split() if " " in text else list(text)
    if not tokens:
        return [""]

    lines, cur = [], tokens[0]
    for t in tokens[1:]:
        sep = " " if " " in text else ""
        test = f"{cur}{sep}{t}"
        box = draw.textbbox((0, 0), test, font=font)
        if (box[2] - box[0]) <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = t
    lines.append(cur)
    return lines


def create_cover(path: Path, title: str, subtitle: str, footer: str):
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), (11, 18, 38))
    d = ImageDraw.Draw(img)

    # Background gradient bands
    bands = [(18, 39, 92), (73, 38, 128), (11, 120, 135)]
    for i, c in enumerate(bands):
        d.rectangle([0, i * h // 3, w, (i + 1) * h // 3], fill=c)

    # Dark overlay for readability
    d.rounded_rectangle([50, 70, 1230, 650], radius=32, fill=(0, 0, 0, 110))

    # Accent ribbon
    d.rounded_rectangle([80, 100, 380, 152], radius=16, fill=(255, 184, 28))
    badge_font = _load_font(30, bold=True)
    d.text((102, 111), "DAILY UPDATE", fill=(20, 20, 20), font=badge_font)

    title_font = _load_font(86, bold=True)
    sub_font = _load_font(42, bold=True)
    footer_font = _load_font(34, bold=False)

    # Title wrapping + shadow
    max_text_width = 1120
    title_lines = _wrap_text(d, title, title_font, max_text_width)
    y = 190
    for line in title_lines[:2]:
        d.text((84, y + 4), line, fill=(0, 0, 0), font=title_font)
        d.text((80, y), line, fill=(255, 255, 255), font=title_font)
        y += 98

    d.text((82, y + 20), subtitle, fill=(245, 245, 255), font=sub_font)
    d.text((82, y + 86), footer, fill=(220, 225, 235), font=footer_font)

    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--cover", required=True)
    ap.add_argument("--title", default="Daily Crypto Podcast")
    ap.add_argument("--subtitle", default="Market update")
    ap.add_argument("--footer", default="Bitcoin • Ethereum • Macro • Risk")
    args = ap.parse_args()

    audio_path = Path(args.audio)
    video_path = Path(args.video)
    cover_path = Path(args.cover)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    create_cover(cover_path, args.title, args.subtitle, args.footer)

    audio = AudioFileClip(str(audio_path))
    clip = ImageClip(str(cover_path), duration=audio.duration).with_audio(audio)
    clip.write_videofile(str(video_path), fps=1, codec="libx264", audio_codec="aac")


if __name__ == "__main__":
    main()
