# MEDI2101B Timetable (GitHub Pages)

Static site that renders your timetable with campus/PBL filters and live status.

## Files
- `index.html` — the site.
- `timetable.json` — primary data source. Commit a fresh copy to update the site.
- `timetable.csv` — optional CSV version; used if JSON is absent.
- `.nojekyll` — disables Jekyll processing for GitHub Pages.
- `tools/convert_excel_to_json.py` — local converter from the Canvas Excel export to JSON/CSV.

## Deploy to GitHub Pages
1. Create a new repo (public or private with Pages enabled).
2. Add the files above to the repo root (keep `index.html` and `timetable.json` side-by-side).
3. GitHub → **Settings** → **Pages** → **Source**: Deploy from branch → `main` → `/root`, then Save.
4. Wait for the green deployment. Your site will be live at `https://<username>.github.io/<repo>/`.

## Update the data
- Export the latest Excel from Canvas.
- Run the converter locally to regenerate `timetable.json` and `timetable.csv`:
  ```bash
  python3 tools/convert_excel_to_json.py "2025 MEDI2101B Timetable - CANVAS-6.xlsx"
  ```
- Commit and push the updated JSON/CSV.
- Refresh the site.

## Local preview
Serve the folder via a local server so the app can auto-fetch data files:
```bash
python3 -m http.server 8000
# open http://localhost:8000
```
Alternatively, drag-and-drop `timetable.json` or `timetable.csv` onto the page, or use the **Load Data** button.
