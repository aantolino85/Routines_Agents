#!/usr/bin/env python3
"""Score ski mountains for the coming weekend using Open-Meteo forecasts.

Usage:
  python personal/scripts/snow_report.py                 # fetch live (needs api.open-meteo.com access)
  python personal/scripts/snow_report.py --print-urls    # print the API URL for each mountain
  python personal/scripts/snow_report.py --from-dir personal/data/raw
        # score from saved JSON files named <mountain_id>.json (fallback when the shell can't reach the API)

Writes a markdown table to stdout and JSON to personal/data/snow_latest.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]          # personal/
CONFIG = ROOT / "config" / "mountains.yaml"
OUT_JSON = ROOT / "data" / "snow_latest.json"
DAILY_VARS = "snowfall_sum,precipitation_sum,temperature_2m_max,temperature_2m_min,wind_speed_10m_max"


def api_url(m: dict) -> str:
    # Kept short on purpose: WebFetch (the fallback path) rejects long URLs.
    params = {
        "latitude": round(m["latitude"], 2),
        "longitude": round(m["longitude"], 2),
        "elevation": m.get("elevation_m", ""),
        "daily": DAILY_VARS,
        "timezone": "auto",
        "past_days": 3,
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
    }
    return "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params, safe=",")


def fetch(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)


def upcoming_weekend(today: dt.date, day_names: list[str]) -> list[dt.date]:
    """Dates of the named days in the next weekend (this weekend if today is Mon-Sat)."""
    names = [d.lower() for d in day_names]
    days = []
    for offset in range(0, 8):
        d = today + dt.timedelta(days=offset)
        if d.strftime("%A").lower() in names:
            days.append(d)
        if days and len(days) == len(names):
            break
    return days


def score_day(daily: dict, idx: int, cfg: dict) -> tuple[float, dict]:
    """Score one day from Open-Meteo daily arrays."""
    snow = daily["snowfall_sum"]
    fresh = sum(v or 0 for v in snow[max(0, idx - 3): idx + 1])        # 72h before + that day
    precip = daily["precipitation_sum"][idx] or 0
    rain = max(0.0, precip - (snow[idx] or 0) / 10)                      # ~10:1 snow-to-liquid
    return score_values(fresh, rain, daily["temperature_2m_max"][idx],
                        daily["temperature_2m_min"][idx], daily["wind_speed_10m_max"][idx] or 0, cfg)


def score_values(fresh, rain, tmax, tmin, wind, cfg) -> tuple[float, dict]:
    """Score one day 0-100: fresh snow up, rain/warmth/cold/wind down."""
    s = 40 + min(fresh, 24) * 2.5                                        # up to +60 for 24"+
    flags = []
    if rain >= cfg["rain_threshold_in"]:
        s -= 25; flags.append("rain")
    if tmax is not None and tmax > cfg["warm_max_f"]:
        s -= 10; flags.append("warm")
    if tmin is not None and tmin < cfg["cold_min_f"]:
        s -= 10; flags.append("frigid")
    if wind > cfg["windy_mph"]:
        s -= 15; flags.append("windy")
    detail = {"fresh_in": round(fresh, 1), "rain_in": round(rain, 2), "high_f": tmax,
              "low_f": tmin, "wind_mph": wind, "flags": flags}
    return max(0.0, min(100.0, s)), detail


def score_mountain(m: dict, data: dict, weekend: list[dt.date], cfg: dict) -> dict:
    daily = data["daily"]
    dates = [dt.date.fromisoformat(t) for t in daily["time"]]
    days = {}
    for d in weekend:
        if d in dates:
            sc, det = score_day(daily, dates.index(d), cfg)
            days[d.strftime("%a")] = {"score": round(sc), **det}
    best = max((v["score"] for v in days.values()), default=0)
    drive_pen = max(0.0, m["drive_hours"] - cfg["drive_penalty_after_hours"]) * 8
    # 72h new snow as of today's forecast window start
    today_idx = min(3, len(daily["snowfall_sum"]) - 1)
    recent = sum(v or 0 for v in daily["snowfall_sum"][: today_idx + 1])
    return {"id": m["id"], "name": m["name"], "state": m["state"], "drive_hours": m["drive_hours"],
            "recent_snow_in": round(recent, 1), "days": days,
            "score": round(max(0, best - drive_pen)), "snow_report_url": m.get("snow_report_url")}


def score_manual(m: dict, entry: dict, cfg: dict) -> dict:
    """Score a mountain from hand-gathered numbers (resort report + summit forecast).

    entry = {status: open|closed, trails: "12/155", recent_snow_in: 3,
             days: {Fri: {snow_in, high_f, low_f, wind_mph, rain_in}, Sat: {...}, Sun: {...}}}
    """
    days, running = {}, float(entry.get("recent_snow_in") or 0)
    for key, d in (entry.get("days") or {}).items():
        running += float(d.get("snow_in") or 0)                          # snow builds through the weekend
        sc, det = score_values(running, float(d.get("rain_in") or 0), d.get("high_f"),
                               d.get("low_f"), float(d.get("wind_mph") or 0), cfg)
        days[key] = {"score": round(sc), **det}
    is_open = str(entry.get("status", "open")).lower() == "open"
    best = max((v["score"] for v in days.values()), default=0) if is_open else 0
    drive_pen = max(0.0, m["drive_hours"] - cfg["drive_penalty_after_hours"]) * 8
    return {"id": m["id"], "name": m["name"], "state": m["state"], "drive_hours": m["drive_hours"],
            "recent_snow_in": round(float(entry.get("recent_snow_in") or 0), 1), "days": days,
            "status": ("Open" if is_open else "Closed") + (f" · {entry['trails']}" if entry.get("trails") else ""),
            "score": round(max(0, best - drive_pen)), "snow_report_url": m.get("snow_report_url")}


def to_markdown(rows: list[dict]) -> str:
    def cell(day):
        if not day:
            return "–"
        f = f" ({', '.join(day['flags'])})" if day["flags"] else ""
        hi = f" · {day['high_f']:.0f}°F" if day.get("high_f") is not None else ""
        return f"{day['fresh_in']}\"{hi}{f}"
    day_keys = list(dict.fromkeys(k for r in rows for k in r["days"]))
    has_status = any("status" in r for r in rows)
    st_h, st_s = (" Status |", "---|") if has_status else ("", "")
    out = [f"| Rank | Mountain | Drive |{st_h} New snow (72h) | " + " | ".join(day_keys) + " | Score |",
           f"|---|---|---|{st_s}---|" + "---|" * len(day_keys) + "---|"]
    for i, r in enumerate(rows, 1):
        cells = " | ".join(cell(r["days"].get(k)) for k in day_keys)
        st = f" {r.get('status', '')} |" if has_status else ""
        out.append(f"| {i} | {r['name']} ({r['state']}) | {r['drive_hours']:.1f}h |{st} "
                   f"{r['recent_snow_in']}\" | {cells} | {r['score']} |")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-dir", type=Path, help="score from saved <id>.json files")
    ap.add_argument("--manual", type=Path, help="score from a hand-gathered YAML file (see score_manual)")
    ap.add_argument("--print-urls", action="store_true")
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    args = ap.parse_args()

    conf = yaml.safe_load(CONFIG.read_text())
    cfg, mountains = conf["scoring"], conf["mountains"]

    if args.print_urls:
        for m in mountains:
            print(f"{m['id']}\t{api_url(m)}")
        return 0

    weekend = upcoming_weekend(args.today, cfg["weekend_days"])
    manual = yaml.safe_load(args.manual.read_text()) if args.manual else None
    rows, failures = [], []
    for m in mountains:
        try:
            if manual is not None:
                if m["id"] not in manual:
                    raise KeyError("missing from manual file")
                rows.append(score_manual(m, manual[m["id"]], cfg))
                continue
            if args.from_dir:
                data = json.loads((args.from_dir / f"{m['id']}.json").read_text())
            else:
                data = fetch(api_url(m))
            rows.append(score_mountain(m, data, weekend, cfg))
        except Exception as e:  # keep going; report what failed
            failures.append((m["id"], str(e)))

    if not rows:
        print("NETWORK_OR_DATA_FAILURE: no mountains scored.", file=sys.stderr)
        for mid, err in failures:
            print(f"  {mid}: {err}", file=sys.stderr)
        print("Fallback: run with --print-urls, fetch each URL, save as personal/data/raw/<id>.json, "
              "then rerun with --from-dir personal/data/raw", file=sys.stderr)
        return 2

    rows.sort(key=lambda r: r["score"], reverse=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"generated": dt.datetime.now().isoformat(timespec="minutes"),
                                    "weekend": [d.isoformat() for d in weekend],
                                    "rows": rows, "failures": failures}, indent=2))
    print(to_markdown(rows))
    for mid, err in failures:
        print(f"\n(warning) {mid} not scored: {err}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
