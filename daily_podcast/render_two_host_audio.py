#!/usr/bin/env python3
import argparse
import json
import random
import re
import subprocess
import tempfile
from pathlib import Path

from moviepy import AudioFileClip, AudioClip, concatenate_audioclips

HOST_A_RE = re.compile(r"^\s*(Host\s*A|Tony)\s*:\s*(.+)$", re.IGNORECASE)
HOST_B_RE = re.compile(r"^\s*(Host\s*B|Kimmi)\s*:\s*(.+)$", re.IGNORECASE)


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
        raise ValueError("No lines found with 'Tony:'/'Kimmi:' (or Host A/Host B) labels")
    return parts


def tts_segment(text: str, voice: str, out_path: Path, rate: str, pitch: str = "+0Hz"):
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
        "--pitch",
        pitch,
        "-o",
        "audio-24khz-48kbitrate-mono-mp3",
    ]
    subprocess.run(cmd, check=True)


def make_silence(seconds: float):
    return AudioClip(lambda t: 0, duration=max(0.0, seconds), fps=24000)


def pause_for_line(text: str, base_pause: float) -> float:
    t = text.strip()
    pause = base_pause
    if any(t.endswith(x) for x in ["?", "？"]):
        pause += 0.10
    if any(t.endswith(x) for x in ["!", "！"]):
        pause += 0.08
    if any(t.endswith(x) for x in ["。", "."]):
        pause += 0.06
    pause += min(0.14, 0.02 * t.count("，") + 0.02 * t.count(","))
    return pause


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="Path to script txt with Host A:/Host B: lines")
    ap.add_argument("--out", required=True, help="Output MP3 path")
    ap.add_argument("--timeline", help="Optional output JSON path for subtitle timeline")
    ap.add_argument("--voice-a", default="en-US-AndrewNeural")
    ap.add_argument("--voice-b", default="en-US-JennyNeural")
    ap.add_argument("--rate-a", default="+3%")
    ap.add_argument("--rate-b", default="+6%")
    ap.add_argument("--pitch-a", default="+0Hz")
    ap.add_argument("--pitch-b", default="+1Hz")
    ap.add_argument("--pause", type=float, default=0.14, help="Base pause between lines in seconds")
    args = ap.parse_args()

    script_text = Path(args.script).read_text(encoding="utf-8")
    parts = parse_script(script_text)

    rng = random.Random(42)
    timeline = []

    with tempfile.TemporaryDirectory(prefix="two-host-tts-") as td:
        temp_dir = Path(td)
        clips = []
        t_cursor = 0.0

        for i, (speaker, text) in enumerate(parts):
            seg = temp_dir / f"seg_{i:04d}.mp3"
            jitter = rng.choice([-1, 0, 1])
            if speaker == "A":
                rate = args.rate_a.replace('%', '')
                rate = f"{int(rate):+d}%" if rate.lstrip('+-').isdigit() else args.rate_a
                pitch = args.pitch_a
                tts_segment(text, args.voice_a, seg, rate, pitch)
            else:
                rate = args.rate_b.replace('%', '')
                rate = f"{int(rate) + jitter:+d}%" if rate.lstrip('+-').isdigit() else args.rate_b
                pitch = args.pitch_b
                tts_segment(text, args.voice_b, seg, rate, pitch)

            seg_clip = AudioFileClip(str(seg))
            seg_duration = float(seg_clip.duration)
            gap = pause_for_line(text, args.pause)

            timeline.append({
                "speaker": speaker,
                "text": text,
                "start": round(t_cursor, 3),
                "end": round(t_cursor + seg_duration, 3),
            })

            clips.append(seg_clip)
            clips.append(make_silence(gap))
            t_cursor += seg_duration + gap

        final = concatenate_audioclips(clips)
        final.write_audiofile(args.out, fps=24000)

        if args.timeline:
            Path(args.timeline).write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")

        for c in clips:
            c.close()
        final.close()


if __name__ == "__main__":
    main()
