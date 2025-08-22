#!/usr/bin/env python3
"""
Convert the Canvas Excel timetable to timetable.json and timetable.csv for the site.

Usage:
  python3 tools/convert_excel_to_json.py "2025 MEDI2101B Timetable - CANVAS-6.xlsx"
Requires:
  pip install pandas openpyxl
"""
import sys, re, json, csv
from datetime import datetime
import pandas as pd

def parse_time_range(time_str):
    s = str(time_str).strip().lower()
    s = s.replace("–","-").replace("—","-")
    s = re.sub(r"\s+"," ", s)
    s = s.replace(".00",":00").replace(".0",":00").replace(".30",":30").replace(".15",":15").replace(".45",":45")
    m = re.match(r"(\d{1,2}[:\.]?\d{0,2}\s*(am|pm))\s*-\s*(\d{1,2}[:\.]?\d{0,2}\s*(am|pm))", s)
    if not m:
        return None, None
    def norm(t):
        t = t.replace(" ","").replace(".00",":00").replace(".30",":30").replace(".15",":15").replace(".45",":45")
        if ":" not in t:
            t = re.sub(r"(\d+)(am|pm)", r"\1:00\2", t)
        return t
    return norm(m.group(1)), norm(m.group(3))

def to_24h(tap):
    m = re.match(r"(\d{1,2}):(\d{2})(am|pm)", tap)
    if not m:
        return None
    hh = int(m.group(1)) % 12
    mm = int(m.group(2))
    if m.group(3) == "pm":
        hh += 12
    return f"{hh:02d}:{mm:02d}"

def convert(path):
    df = pd.read_excel(path, sheet_name=0)
    df.columns = [c.strip().replace("\n"," ").replace("  "," ") for c in df.columns]

    events = []
    for _, row in df.iterrows():
        date_val = row.get("Date")
        time_val = row.get("Time")
        if pd.isna(date_val) or pd.isna(time_val):
            continue
        start_ap, end_ap = parse_time_range(time_val)
        if not start_ap or not end_ap:
            continue
        start_hm, end_hm = to_24h(start_ap), to_24h(end_ap)
        if isinstance(date_val, pd.Timestamp):
            date_iso = date_val.strftime("%Y-%m-%d")
        else:
            try:
                date_iso = pd.to_datetime(date_val).strftime("%Y-%m-%d")
            except Exception:
                continue
        start_iso, end_iso = f"{date_iso}T{start_hm}", f"{date_iso}T{end_hm}"

        campus_raw = str(row.get("Campus","")).strip()
        campus_map = {"CAL":"Callaghan","CC":"CCS","CAL/CC":"Both","CC/CAL":"Both"}
        campus = campus_map.get(campus_raw, campus_map.get(str(campus_raw).split("/")[0], str(campus_raw)))

        group_raw = str(row.get("Group","")).strip()
        groups = [g.strip() for g in re.split(r"[,\s]+", group_raw) if g.strip()]
        groups = [g for g in groups if re.match(r"^[A-P]$", g)]
        if not groups:
            groups = ["ALL"]

        session = str(row.get("Session","")).strip()
        domain = str(row.get("Domain","")).strip()
        activity = str(row.get("Activity Type","")).strip()
        venue_col = "Primary Venue/ Zoom Link" if "Primary Venue/ Zoom Link" in df.columns else \
                    "Primary Venue/Zoom Link" if "Primary Venue/Zoom Link" in df.columns else ""
        venue = str(row.get(venue_col,"")).strip()
        staff = str(row.get("Staff","")).strip()
        title = session if session else f"{domain} {activity}".strip()

        events.append({
            "date": date_iso,
            "start": start_iso,
            "end": end_iso,
            "title": title,
            "domain": domain,
            "activity": activity,
            "campus": campus,
            "groups": groups,
            "venue": venue,
            "staff": staff
        })

    # Write outputs
    with open("timetable.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    with open("timetable.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","start","end","title","domain","activity","campus","groups","venue","staff"])
        for ev in events:
            w.writerow([ev["date"], ev["start"], ev["end"], ev["title"], ev["domain"], ev["activity"],
                        ev["campus"], ";".join(ev["groups"]), ev["venue"], ev["staff"]])
    print(f"Wrote timetable.json ({len(events)} events) and timetable.csv")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/convert_excel_to_json.py <excel_path>")
        sys.exit(1)
    convert(sys.argv[1])
