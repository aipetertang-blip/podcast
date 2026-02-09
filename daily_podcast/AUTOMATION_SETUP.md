# Daily Podcast Automation Setup (YouTube)

## What is already scheduled
- Daily generation at 12:00 PM ET for:
  - hot-topics brief
  - 2-host podcast script (~5 min)
  - YouTube package (title/description/tags)
  - TTS audio

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
