#!/usr/bin/env python3
import argparse
from pathlib import Path
from moviepy import ImageClip, AudioFileClip
from PIL import Image, ImageDraw


def create_cover(path: Path, title: str, subtitle: str, footer: str):
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), (16, 18, 27))
    d = ImageDraw.Draw(img)

    bands = [(27, 52, 122), (84, 38, 132), (16, 112, 120)]
    for i, c in enumerate(bands):
        d.rectangle([0, i * h // 3, w, (i + 1) * h // 3], fill=c)

    d.text((80, 210), title, fill="white")
    d.text((80, 280), subtitle, fill="white")
    d.text((80, 335), footer, fill="white")

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
