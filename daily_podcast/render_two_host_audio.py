#!/usr/bin/env python3
import argparse
import re
import subprocess
import tempfile
from pathlib import Path

from moviepy import AudioFileClip, AudioClip, concatenate_audioclips

HOST_A_RE = re.compile(r"^\s*(Host\s*A)\s*:\s*(.+)$", re.IGNORECASE)
HOST_B_RE = re.compile(r"^\s*(Host\s*B)\s*:\s*(.+)$", re.IGNORECASE)


def parse_script(script_text: str):
    parts = []
    for raw in script_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        ma = HOST_A_RE.match(line)
        if ma:
            parts.append(("A", ma.group(2).strip()))
            continue
        mb = HOST_B_RE.match(line)
        if mb:
            parts.append(("B", mb.group(2).strip()))
            continue
    if not parts:
        raise ValueError("No lines found with 'Host A:' / 'Host B:' labels")
    return parts


def tts_segment(text: str, voice: str, out_path: Path, rate: str):
    cmd = [
        "npx",
        "-y",
        "node-edge-tts",
        "-t",
        text,
        "-f",
        str(out_path),
        "-v",
        voice,
        "-r",
        rate,
        "-o",
        "audio-24khz-48kbitrate-mono-mp3",
    ]
    subprocess.run(cmd, check=True)


def make_silence(seconds: float):
    return AudioClip(lambda t: 0, duration=max(0.0, seconds), fps=24000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="Path to script txt with Host A:/Host B: lines")
    ap.add_argument("--out", required=True, help="Output MP3 path")
    ap.add_argument("--voice-a", default="en-US-AndrewNeural")
    ap.add_argument("--voice-b", default="en-US-JennyNeural")
    ap.add_argument("--rate-a", default="+0%")
    ap.add_argument("--rate-b", default="+2%")
    ap.add_argument("--pause", type=float, default=0.18, help="Pause between lines in seconds")
    args = ap.parse_args()

    script_text = Path(args.script).read_text(encoding="utf-8")
    parts = parse_script(script_text)

    with tempfile.TemporaryDirectory(prefix="two-host-tts-") as td:
        temp_dir = Path(td)
        clips = []
        for i, (speaker, text) in enumerate(parts):
            seg = temp_dir / f"seg_{i:04d}.mp3"
            if speaker == "A":
                tts_segment(text, args.voice_a, seg, args.rate_a)
            else:
                tts_segment(text, args.voice_b, seg, args.rate_b)
            clips.append(AudioFileClip(str(seg)))
            clips.append(make_silence(args.pause))

        final = concatenate_audioclips(clips)
        final.write_audiofile(args.out, fps=24000)

        for c in clips:
            c.close()
        final.close()


if __name__ == "__main__":
    main()
