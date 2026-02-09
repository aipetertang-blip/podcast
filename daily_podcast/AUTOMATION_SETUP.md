# Daily Podcast Automation Setup (YouTube)

## What is already scheduled
- Daily generation at 12:00 PM ET for:
  - hot-topics brief
  - 2-host podcast script (~5 min)
  - YouTube package (title/description/tags)
  - dual-voice audio + upload (English)
  - Chinese version (same core content) + upload

## To enable fully automated YouTube upload
You must provide YouTube API OAuth credentials once.

### 1) Create Google OAuth client
- Google Cloud Console -> APIs & Services
- Enable **YouTube Data API v3**
- Create OAuth client (Desktop app)
- Save credentials JSON

### 2) Place credentials file
- Save as:
  `/home/ttang/.openclaw/workspace/daily_podcast/google_oauth_client.json`

### 3) First-time OAuth consent
- Run uploader setup once (interactive browser sign-in)
- This creates and caches upload token for future automatic uploads

### 4) Set defaults
- Copy `youtube_upload_config.example.json` to `youtube_upload_config.json`
- Fill in channel + defaults

## Notes
- Without OAuth credentials, generation works but upload cannot be fully automated.
- YouTube upload requires a video container. Audio is wrapped into an MP4 using `make_podcast_video.py` before upload.
- Two-host audio: `render_two_host_audio.py` synthesizes Host A/Host B with different voices.
- Daily cleanup: `cleanup_old_content.py` removes generated media older than 7 days.
