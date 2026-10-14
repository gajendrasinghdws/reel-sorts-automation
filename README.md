# Reel-Sorts Automation

A free-tier starter for:
- Managing multiple Instagram usernames and manual public Reel URLs.
- Downloading one queued Reel per day.
- Saving videos into a Google Drive folder named `Reel-Sorts`.
- Uploading one pending video to YouTube daily at 07:00 Asia/Kolkata.
- Preventing duplicate downloads/uploads with Supabase.
- Deleting a successfully uploaded Drive video after 24 hours.
- No Instagram passwords.

## Architecture

Dashboard: static HTML/CSS/JS (GitHub Pages)
Database: Supabase Postgres + Auth/RLS
Automation: Python + GitHub Actions
Storage: Google Drive API
YouTube: YouTube Data API v3
Video tools: yt-dlp + FFmpeg

## Important Instagram note

The project intentionally does NOT collect Instagram passwords.

`yt-dlp` is used as the default public-URL/profile extraction adapter. Instagram can change or restrict public extraction at any time, so the Instagram adapter is isolated in `automation/instagram.py`. If a source stops working, replace that adapter with an API/compliant source without changing the rest of the system.

Only download/use content you are authorized to use.

## 1. Supabase

1. Create a Supabase project.
2. Open SQL Editor.
3. Run `supabase/schema.sql`.
4. In Authentication, enable Email provider.
5. Create your dashboard user in Supabase Auth.
6. Copy:
   - Project URL
   - Publishable key (or legacy anon key)

Do NOT put a `service_role`/secret key in the dashboard.

## 2. Google Cloud / OAuth

Create a Google Cloud project and enable:
- Google Drive API
- YouTube Data API v3

Configure Google Auth Platform and create a Desktop OAuth client.
Download its JSON as:

`oauth/credentials.json`

Install Python dependencies:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r automation/requirements.txt
```

Run:

```bash
python oauth/setup_google_oauth.py
```

A browser will open. Authorize the Google account that owns the Drive folder and YouTube channel.

The script creates `oauth/token.json`.

## 3. Google Drive folder

Create a folder in Drive called:

`Reel-Sorts`

Copy its folder ID from the Drive URL:

`https://drive.google.com/drive/folders/FOLDER_ID`

Set GitHub Secret:

`DRIVE_FOLDER_ID`

## 4. GitHub repository secrets

Add these repository secrets:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` (backend only; never expose it to the browser)
- `GOOGLE_TOKEN_JSON` (entire contents of oauth/token.json)
- `DRIVE_FOLDER_ID`

Optional:
- `MAX_DOWNLOAD_SECONDS` (default 1800)

## 5. Dashboard

Edit:

`dashboard/config.js`

Set:

```js
window.REEL_SORTS_CONFIG = {
  supabaseUrl: "https://YOUR_PROJECT.supabase.co",
  supabasePublishableKey: "YOUR_PUBLISHABLE_KEY"
};
```

The publishable key is intended for frontend use when RLS is configured correctly.

For GitHub Pages:
- Push the repository.
- Settings -> Pages -> Deploy from branch.
- Select the branch and `/dashboard` only if using a Pages configuration that supports it, or copy dashboard files to the Pages root.

For a simple Pages deployment, the included GitHub Pages workflow deploys `dashboard/`.

## 6. Local smoke tests

Run:

```bash
python automation/main.py --help
python automation/main.py cleanup
```

The actual `download` and `upload` commands require valid Google/Supabase credentials.

## Scheduled workflows

- `download.yml`: every day at 06:30 IST
- `upload.yml`: every day at 07:00 IST
- `cleanup.yml`: every day at 07:30 IST

GitHub Actions supports timezone-aware schedules. If a scheduled job is delayed by GitHub, it can start later than the nominal schedule.

## YouTube title

The default title generator is intentionally free and deterministic:
- Uses caption/title metadata when available.
- Otherwise uses filename/description text.
- Cleans and truncates to YouTube's title limit.

No paid AI API is required.

## Flow

Instagram/manual URL
 -> duplicate check
 -> download
 -> SHA-256 hash check
 -> Google Drive/Reel-Sorts
 -> database record
 -> next 07:00 upload
 -> YouTube
 -> mark uploaded
 -> after 24h, delete Drive file

If YouTube upload fails, the Drive file is NOT deleted.
