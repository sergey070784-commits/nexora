# Nexora Level 1 — Cloudinary photo transfer

## Files
- `index.html` — Level 1 with photo upload + site JSON save flow.
- `style.css` — stylesheet.
- `cloudinary-worker.js` — code for the separate Cloudflare Cloudinary Worker.

## Cloudinary Worker setup

Create a new Cloudflare Worker named `cloudinary-worker` and paste the contents of
`cloudinary-worker.js`, then Deploy.

Add these Production variables/secrets in Worker Settings → Variables and Secrets:

- `CLOUDINARY_CLOUD_NAME` — ordinary variable; Cloudinary cloud name only.
- `CLOUDINARY_API_KEY` — ordinary variable; Cloudinary API key.
- `CLOUDINARY_API_SECRET` — Secret; Cloudinary API secret. Do not put this in browser code.

The frontend is configured to call:
`https://site-data-cloudinary-worker.sergey070784.workers.dev/`

If Cloudflare gives the Worker a different URL, change that URL in `index.html`
in the `fetch()` call for the photo upload.

## Flow

When the user clicks "הסכם":
1. If a photo was selected, Level 1 sends `file` + `session_id` as multipart FormData.
2. Cloudinary Worker signs the upload and uploads the file to `nexora/<session_id>`.
3. Worker returns `secure_url`.
4. Level 1 places that URL into `siteData.site.photo`.
5. Level 1 sends the complete JSON to the existing Site Data Worker.
6. Supabase stores the Cloudinary URL in `photo`.

If no photo was selected, step 1–3 are skipped and the JSON is saved as before.
