#!/usr/bin/env python3
import argparse
import json
import tempfile
from pathlib import Path

from moviepy import AudioFileClip, CompositeVideoClip, ImageClip
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

    bands = [(18, 39, 92), (73, 38, 128), (11, 120, 135)]
    for i, c in enumerate(bands):
        d.rectangle([0, i * h // 3, w, (i + 1) * h // 3], fill=c)

    d.rounded_rectangle([50, 70, 1230, 650], radius=32, fill=(0, 0, 0, 110))
    d.rounded_rectangle([80, 100, 380, 152], radius=16, fill=(255, 184, 28))

    badge_font = _load_font(30, bold=True)
    d.text((102, 111), "DAILY UPDATE", fill=(20, 20, 20), font=badge_font)

    title_font = _load_font(86, bold=True)
    sub_font = _load_font(42, bold=True)
    footer_font = _load_font(34, bold=False)

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


def _subtitle_image(path: Path, text: str, speaker: str, width=1100, height=130):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, width, height], radius=20, fill=(0, 0, 0, 170))

    speaker_color = (255, 199, 84) if speaker == "A" else (144, 216, 255)
    speaker_font = _load_font(34, bold=True)
    text_font = _load_font(40, bold=True)

    label = "Tony:" if speaker == "A" else "Kimmi:"
    d.text((28, 16), label, fill=speaker_color, font=speaker_font)

    wrapped = _wrap_text(d, text, text_font, width - 120)[:2]
    y = 18
    for i, line in enumerate(wrapped):
        d.text((95, y + i * 44), line, fill=(255, 255, 255), font=text_font)

    img.save(path)


def add_subtitles(base_clip, timeline_path: Path):
    data = json.loads(timeline_path.read_text(encoding="utf-8"))
    overlay = [base_clip]

    with tempfile.TemporaryDirectory(prefix="subtitle-img-") as td:
        td_path = Path(td)
        for i, row in enumerate(data):
            start = float(row.get("start", 0))
            end = float(row.get("end", start + 1))
            if end <= start:
                continue
            text = str(row.get("text", "")).strip()
            if not text:
                continue
            speaker = str(row.get("speaker", "A")).upper()

            img_path = td_path / f"sub_{i:04d}.png"
            _subtitle_image(img_path, text, speaker)
            c = (
                ImageClip(str(img_path))
                .with_start(start)
                .with_duration(end - start)
                .with_position(("center", 560))
            )
            overlay.append(c)

        return CompositeVideoClip(overlay, size=base_clip.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--cover", required=True)
    ap.add_argument("--title", default="Daily Crypto Podcast")
    ap.add_argument("--subtitle", default="Market update")
    ap.add_argument("--footer", default="Bitcoin • Ethereum • Macro • Risk")
    ap.add_argument("--timeline", help="Optional subtitle timeline JSON from render_two_host_audio.py")
    args = ap.parse_args()

    audio_path = Path(args.audio)
    video_path = Path(args.video)
    cover_path = Path(args.cover)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    create_cover(cover_path, args.title, args.subtitle, args.footer)

    audio = AudioFileClip(str(audio_path))
    base = ImageClip(str(cover_path), duration=audio.duration).with_audio(audio)

    final_clip = base
    if args.timeline:
        tl = Path(args.timeline)
        if tl.exists():
            final_clip = add_subtitles(base, tl)
            final_clip = final_clip.with_audio(audio)

    final_clip.write_videofile(str(video_path), fps=1, codec="libx264", audio_codec="aac")


if __name__ == "__main__":
    main()
