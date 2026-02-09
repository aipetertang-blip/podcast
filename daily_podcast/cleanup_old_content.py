#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path


def should_delete(path: Path) -> bool:
    name = path.name.lower()
    keep_exact = {
        "google_oauth_client.json",
        "youtube_token.json",
        "youtube_uploader.py",
        "make_podcast_video.py",
        "render_two_host_audio.py",
        "cleanup_old_content.py",
        "automation_setup.md",
        "project_context.md",
        "youtube_upload_config.example.json",
    }
    if name in keep_exact:
        return False

    delete_ext = {".mp3", ".mp4", ".wav", ".m4a", ".png", ".txt", ".md", ".json"}
    generated_prefixes = (
        "daily_podcast_",
        "podcast_script_",
        "hot_topics_brief_",
        "youtube_metadata_",
    )

    if name.startswith("cover"):
        return True

    return path.suffix.lower() in delete_ext and any(name.startswith(p) for p in generated_prefixes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()

    root = Path(args.dir)
    cutoff = time.time() - args.days * 86400

    deleted = []
    kept = []

    for p in root.iterdir():
        if not p.is_file():
            continue
        if not should_delete(p):
            kept.append(str(p))
            continue
        if p.stat().st_mtime < cutoff:
            p.unlink(missing_ok=True)
            deleted.append(str(p))

    print(json.dumps({
        "dir": str(root),
        "days": args.days,
        "deletedCount": len(deleted),
        "deleted": deleted,
    }, indent=2))


if __name__ == "__main__":
    main()
