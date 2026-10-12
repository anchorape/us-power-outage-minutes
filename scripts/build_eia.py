"""Parse EIA Electric Power Annual Tables 11.3 and 11.4 (downloaded HTML) into CSVs and a JSON summary.
Usage: python -I build_eia.py <eia_dir> <out_repo_dir>"""
import csv, html, json, os, re, sys

eia_dir, out = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(out, "data"), exist_ok=True)

DIVISIONS = {"New England", "Middle Atlantic", "East North Central", "West North Central", "South Atlantic",
             "East South Central", "West South Central", "Mountain", "Pacific Contiguous", "Pacific Noncontiguous"}
SERIES = ["ieee_all_events", "ieee_without_major_events", "ieee_loss_of_supply_removed",
          "any_method_all_events", "any_method_without_major_events"]
YEARS = list(range(2024, 2013, -1))


def rows(name):
    h = open(os.path.join(eia_dir, name), encoding="utf-8", errors="replace").read()
    out_rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", h, re.S):
        c = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        if len(c) >= 10 and c[0] != "Census Divisionand State":
            out_rows.append(c)
    return out_rows


def num(s):
    s = s.replace(",", "").replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def kind(area):
    return "us_total" if area == "U.S. Total" else ("census_division" if area in DIVISIONS else "state")


# Table 11.4: 55 values = 5 series x 11 years (2024..2014)
long_rows, saidi = [], {}
for r in rows("11_04.html"):
    area, vals = r[0], r[1:]
    assert len(vals) == 55, (area, len(vals))
    for si, s in enumerate(SERIES):
        for yi, y in enumerate(YEARS):
            v = num(vals[si * 11 + yi])
            if v is None:
                continue
            long_rows.append([area, kind(area), y, s, v])
            saidi.setdefault(area, {}).setdefault(s, {})[y] = v

with open(os.path.join(out, "data", "saidi_by_state_2014_2024.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["area", "area_type", "year", "series", "saidi_minutes"])
    w.writerows(sorted(long_rows, key=lambda x: (x[0], x[3], x[2])))

# Table 11.3: 14 values = pct reported (24,23), SAIDI all (24,23), SAIFI all, CAIDI all, SAIDI w/o, SAIFI w/o, CAIDI w/o
t3, metrics = [], {}
for r in rows("11_03.html"):
    area, v = r[0], r[1:]
    assert len(v) == 14, (area, len(v))
    for yi, y in enumerate([2024, 2023]):
        rec = [num(v[0 + yi]), num(v[2 + yi]), num(v[4 + yi]), num(v[6 + yi]), num(v[8 + yi]), num(v[10 + yi]), num(v[12 + yi])]
        t3.append([area, kind(area), y] + rec)
        metrics.setdefault(area, {})[y] = rec

with open(os.path.join(out, "data", "reliability_metrics_2023_2024.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["area", "area_type", "year", "percent_customers_reported", "saidi_minutes_all_events", "saifi_all_events",
                "caidi_minutes_all_events", "saidi_minutes_without_major_events", "saifi_without_major_events",
                "caidi_minutes_without_major_events"])
    w.writerows(t3)

# cross-check: 11.3 SAIDI 2024 all events (any method) == 11.4 any_method_all_events 2024
mismatch = [a for a in metrics if metrics[a][2024][1] != saidi[a]["any_method_all_events"].get(2024)]
assert not mismatch, mismatch

# summary for the page (states + DC only, any method series)
states = []
for a, s in saidi.items():
    if kind(a) != "state":
        continue
    allv = s["any_method_all_events"]
    wo = s["any_method_without_major_events"]
    yrs = [y for y in YEARS if y in allv]
    worst = max(yrs, key=lambda y: allv[y])
    states.append({
        "state": a,
        "y2024": allv.get(2024), "y2023": allv.get(2023),
        "wo2024": wo.get(2024),
        "avg": round(sum(allv[y] for y in yrs) / len(yrs), 1), "nyears": len(yrs),
        "worst_year": worst, "worst": allv[worst],
        "pct_reported_2024": metrics[a][2024][0],
        "saifi2024": metrics[a][2024][2],
        "series": {str(y): allv[y] for y in yrs},
    })
us = {"any2024": saidi["U.S. Total"]["any_method_all_events"], "ieee": saidi["U.S. Total"]["ieee_all_events"],
      "any_wo": saidi["U.S. Total"]["any_method_without_major_events"]}
top = sorted(((st["state"], y, v) for st in states for y, v in st["series"].items()), key=lambda x: -x[2])[:12]
json.dump({"states": sorted(states, key=lambda x: -x["y2024"]), "us": us, "top_state_years": top},
          open(os.path.join(out, "data", "summary.json"), "w", encoding="utf-8"), indent=1)
print("long rows", len(long_rows), "t3 rows", len(t3), "states", len(states))
print("US any 2024", us["any2024"][2024], "IEEE 2024", us["ieee"][2024], "any max year", max(us["any2024"], key=us["any2024"].get), "ieee max year", max(us["ieee"], key=us["ieee"].get))
print("top", top[:6])
print("low coverage 2024", [(s["state"], s["pct_reported_2024"]) for s in states if s["pct_reported_2024"] is not None and s["pct_reported_2024"] < 80])
