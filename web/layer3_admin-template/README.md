# Nexora Admin Template — Layer 3

Universal two-page admin frontend. No slot is hardcoded in the browser.

## Current stage

1. `index.html` collects the user's email. Name and phone are optional and may be left empty.
2. JavaScript sends the entered values as JSON to `POST /api/admin/login`.
3. Python Admin must perform the real lookup (`site_admin_links` → `admin_url` → GitHub config → `slot_id`) and return the site's existing data for that slot.
4. Only after a successful response containing `slot_id` and `site`, the browser opens `editor.html`.
5. The editor renders the site and all editing controls work locally in the browser.
6. The green Save button is visible and clickable, but intentionally does not write to Supabase yet. It displays a notice. OTP verification and the authorized save request will be added before enabling persistence.

## Files

- `index.html` — email login page (name and phone optional).
- `editor.html` — Layer 2 visual template with Layer 1 editing dialogs.
- `editor.js` — local editing and login API request.
- `style.css` — editor styles.
- `api-contract.json` — current frontend/backend contract.

## Python API contract

### `POST /api/admin/login`

Request JSON (name and phone may be empty):

```json
{"name":"","email":"user@example.com","phone":""}
```

Successful response JSON:

```json
{"success":true,"slot_id":"slot_3","site":{"name":"...","profession":"..."},"image":"https://..."}
```

Python must resolve `site_admin_links` → `admin_url` → GitHub config → `slot_id`, then read that slot from `site_data_users` and return the existing text data plus image URL.

The browser does not choose or calculate the slot. It only stores the `slot_id` returned by Python for the current editor session.

## Local server requirement

The frontend calls `/api/admin/login` on the same origin. The Python Admin server must serve these static files or provide a same-origin reverse proxy for `/api/`. A static-only server such as `python -m http.server 8000` cannot handle this API route by itself.

## Save stage

`POST /api/admin/save` is not called yet. The green button is intentionally a placeholder action until the OTP flow is implemented. Current editing is local to the browser session; refreshing or leaving the page discards unsaved changes.
