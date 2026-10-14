# Setup checklist

## A. Supabase
1. Create project.
2. Run `supabase/schema.sql`.
3. Enable Email Auth.
4. Create one user for dashboard.
5. Copy Project URL and Publishable Key to `dashboard/config.js`.

## B. Google
1. Create Cloud project.
2. Enable Drive API and YouTube Data API.
3. Configure Google Auth Platform.
4. Create Desktop OAuth client.
5. Download JSON to `oauth/credentials.json`.
6. Run `python oauth/setup_google_oauth.py`.
7. Add the resulting `token.json` as GitHub secret `GOOGLE_TOKEN_JSON`.

## C. GitHub secrets
Add:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY
- GOOGLE_TOKEN_JSON
- DRIVE_FOLDER_ID

Never put `SUPABASE_SERVICE_ROLE_KEY` or Google token JSON into dashboard files.

## D. Pages
Push to `main`. GitHub Pages workflow deploys the dashboard.

## E. First test
Run GitHub Actions manually:
1. Download one Reel
2. Upload one Reel
3. Cleanup

Do the first run with a short, authorized test video.
