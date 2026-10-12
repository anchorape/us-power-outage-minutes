"""Render index.html and README.md for the outage-minutes dataset from data/summary.json.
Usage: python -I build_page.py <repo_dir>"""
import html, json, os, sys

repo = sys.argv[1]
S = json.load(open(os.path.join(repo, "data", "summary.json"), encoding="utf-8"))
states, us, top = S["states"], S["us"], S["top_state_years"]
URL = "https://anchorape.github.io/us-power-outage-minutes/"
SGR = "https://www.solargenreview.com"
T113 = "https://www.eia.gov/electricity/annual/table.php?t=epa_11_03.html"
T114 = "https://www.eia.gov/electricity/annual/table.php?t=epa_11_04.html"


def h(m):
    return f"{m / 60:.1f}"


def fmt(m):
    return f"{m:,.1f}"


def spark(series):
    ys = [series[str(y)] for y in range(2014, 2025) if str(y) in series]
    xs = [y for y in range(2014, 2025) if str(y) in series]
    lo, hi = min(ys), max(ys)
    pts = []
    for x, y in zip(xs, ys):
        px = 2 + (x - 2014) * 9.6
        py = 22 - (0 if hi == lo else (y - lo) / (hi - lo)) * 20
        pts.append(f"{px:.1f},{py:.1f}")
    last = pts[-1].split(",")
    return (f'<svg class="sp" viewBox="0 0 100 24" width="100" height="24" aria-hidden="true">'
            f'<polyline points="{" ".join(pts)}"/><circle cx="{last[0]}" cy="{last[1]}" r="2"/></svg>')


any24, any23 = us["any2024"]["2024"], us["any2024"]["2023"]
ieee24 = us["ieee"]["2024"]
wo24 = us["any_wo"]["2024"]
share_major = round(100 * (1 - wo24 / any24))
any_max_year = max(us["any2024"], key=lambda k: us["any2024"][k])
ieee_max_year = max(us["ieee"], key=lambda k: us["ieee"][k])
assert any_max_year == "2024" and ieee_max_year == "2024"
low_cov = [s for s in states if s["pct_reported_2024"] is not None and s["pct_reported_2024"] < 80]
low_cov_txt = ", ".join(f'{s["state"]} ({s["pct_reported_2024"]:.1f}%)' for s in sorted(low_cov, key=lambda s: s["pct_reported_2024"]))
worst24 = states[0]
best24 = states[-1]
over24h = [s["state"] for s in states if s["y2024"] >= 1440]

rows = []
for i, s in enumerate(states, 1):
    share = "" if not s["wo2024"] else f'{round(100 * (1 - s["wo2024"] / s["y2024"]))}%'
    rows.append(
        f'<tr><td data-v="{i}">{i}</td><td data-v="{html.escape(s["state"])}">{html.escape(s["state"])}</td>'
        f'<td data-v="{s["y2024"]}">{h(s["y2024"])}</td>'
        f'<td data-v="{s["wo2024"] or 0}">{h(s["wo2024"]) if s["wo2024"] else "n/a"}</td>'
        f'<td data-v="{share[:-1] if share else -1}">{share or "n/a"}</td>'
        f'<td data-v="{s["y2023"] or 0}">{h(s["y2023"]) if s["y2023"] else "n/a"}</td>'
        f'<td data-v="{s["avg"]}">{h(s["avg"])}</td>'
        f'<td data-v="{s["worst"]}">{h(s["worst"])} ({s["worst_year"]})</td>'
        f'<td class="nosort">{spark(s["series"])}</td></tr>')

top_rows = "".join(f'<tr><td>{html.escape(a)}</td><td>{y}</td><td>{fmt(v)}</td><td>{h(v)}</td></tr>' for a, y, v in top)

desc = (f"Average hours without power for every US state and DC, 2014 to 2024, from EIA's SAIDI tables: "
        f"{h(any24)} hours nationally in 2024. Sortable table and free CSV downloads.")

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>US Power Outage Minutes by State, 2014 to 2024 (EIA SAIDI Data)</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{URL}">
<meta property="og:title" content="US Power Outage Minutes by State, 2014 to 2024">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{URL}">
<script type="application/ld+json">
{json.dumps({"@context": "https://schema.org", "@type": "Dataset",
             "name": "US power outage minutes (SAIDI) by state, 2014 to 2024",
             "description": desc, "url": URL,
             "license": "https://creativecommons.org/publicdomain/zero/1.0/",
             "temporalCoverage": "2014/2024", "spatialCoverage": "United States",
             "isBasedOn": [T113, T114],
             "creator": {"@type": "Organization", "name": "SolarGenReview", "url": SGR},
             "distribution": [
                 {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": URL + "data/saidi_by_state_2014_2024.csv"},
                 {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": URL + "data/reliability_metrics_2023_2024.csv"}]},
            indent=1)}
</script>
<style>
:root{{--ink:#1d2430;--muted:#5b6574;--line:#dfe3e8;--bg:#fbfaf7;--card:#fff;--acc:#c2410c;--acc2:#0f766e}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
main{{max-width:1040px;margin:0 auto;padding:28px 16px 60px}}
h1{{font-size:clamp(1.6rem,4vw,2.3rem);line-height:1.2;margin:.2em 0 .4em}}
h2{{font-size:1.3rem;margin:2em 0 .5em}}
p,li{{max-width:72ch}}
.kick{{color:var(--acc);font-weight:600;letter-spacing:.04em;text-transform:uppercase;font-size:.8rem}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:22px 0}}
.stat{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}}
.stat b{{display:block;font-size:1.7rem;line-height:1.1;color:var(--acc)}}
.stat span{{color:var(--muted);font-size:.9rem}}
.wrap{{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px}}
table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;font-size:.93rem}}
th,td{{padding:8px 10px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}}
th:nth-child(2),td:nth-child(2){{text-align:left}}
thead th{{background:#f3f1ec;position:sticky;top:0;cursor:pointer;user-select:none}}
thead th.nosort{{cursor:default}}
thead th[aria-sort]::after{{content:" \\2195";color:var(--muted)}}
tbody tr:hover{{background:#faf6ef}}
.sp polyline{{fill:none;stroke:var(--acc2);stroke-width:1.6}}
.sp circle{{fill:var(--acc)}}
.note{{color:var(--muted);font-size:.9rem}}
dl dt{{font-weight:600;margin-top:.8em}}
dl dd{{margin:0 0 0 0;max-width:72ch}}
a{{color:var(--acc2)}}
code{{background:#efece5;padding:1px 5px;border-radius:4px;font-size:.9em}}
footer{{margin-top:48px;border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:.88rem}}
</style>
</head>
<body>
<main>
<p class="kick">Open data</p>
<h1>US power outage minutes by state, 2014 to 2024</h1>
<p>The average US electricity customer went <strong>{fmt(any24)} minutes, about {h(any24)} hours, without power in 2024</strong>, according to the U.S. Energy Information Administration's "any method" series. That is the highest of the eleven years EIA publishes by state, and up from {fmt(any23)} minutes in 2023. On EIA's IEEE-standard series, which covers fewer utilities, the 2024 figure was {fmt(ieee24)} minutes ({h(ieee24)} hours), also the highest since 2014.</p>
<p>Most of 2024's total came from major events such as hurricanes and ice storms. With major event days removed, the national figure was {fmt(wo24)} minutes ({h(wo24)} hours), so about {share_major}% of the year's outage time fell on major event days.</p>

<div class="stats">
<div class="stat"><b>{h(any24)} h</b><span>US average without power, 2024 (all events)</span></div>
<div class="stat"><b>{h(wo24)} h</b><span>US average, 2024, without major event days</span></div>
<div class="stat"><b>{h(worst24["y2024"])} h</b><span>Highest state in 2024: {html.escape(worst24["state"])}</span></div>
<div class="stat"><b>{len(over24h)}</b><span>States above 24 hours in 2024</span></div>
</div>

<h2>Hours without power by state</h2>
<p class="note">Average hours of sustained interruption per customer (SAIDI in minutes, divided by 60), EIA "any method" series. Click a column to sort. The trend line runs 2014 to 2024 on each state's own scale; the dot is 2024. "Share from major events" is the part of 2024's total that disappears when major event days are removed.</p>
<div class="wrap">
<table id="t">
<thead><tr><th aria-sort="none">#</th><th aria-sort="none">State</th><th aria-sort="none">2024 hours</th><th aria-sort="none">2024 without major events</th><th aria-sort="none">Share from major events</th><th aria-sort="none">2023 hours</th><th aria-sort="none">Average 2014-2024</th><th aria-sort="none">Worst year</th><th class="nosort">2014 to 2024</th></tr></thead>
<tbody>
{"".join(rows)}
</tbody>
</table>
</div>
<p class="note">Lowest in 2024: {html.escape(best24["state"])}, {h(best24["y2024"])} hours. Coverage caveat: the utilities reporting in 2024 served under 80% of customers in {low_cov_txt}, so those states' figures describe fewer customers. Averages use every year EIA publishes for the state.</p>

<h2>The longest state-years since 2014</h2>
<div class="wrap">
<table>
<thead><tr><th class="nosort" style="text-align:left">State</th><th class="nosort">Year</th><th class="nosort">Minutes (SAIDI)</th><th class="nosort">Hours</th></tr></thead>
<tbody>{top_rows}</tbody>
</table>
</div>

<h2>What the numbers mean</h2>
<dl>
<dt>SAIDI (System Average Interruption Duration Index)</dt>
<dd>The total minutes of sustained interruption the average customer of a utility experiences in a year. EIA aggregates the utilities in each state.</dd>
<dt>SAIFI and CAIDI</dt>
<dd>SAIFI is the average number of sustained interruptions per customer in the year; CAIDI is the average length of one interruption in minutes (SAIDI divided by SAIFI). Both are in the 2023 and 2024 file below.</dd>
<dt>Major event days</dt>
<dd>Days whose outage time is far above a utility's normal range, identified under the IEEE 1366 standard. Storms and similar events drive them. The "without major event days" figures show routine reliability; the "all events" figures show what customers actually lived through.</dd>
<dt>"Any method" and IEEE series</dt>
<dd>EIA publishes one series from utilities that follow the IEEE 1366 standard and an "any method" series that also includes utilities calculating their indices another way. The any-method series covers more customers, which is why this page leads with it. Both are in the full CSV.</dd>
</dl>

<h2>Download the data</h2>
<ul>
<li><a href="data/saidi_by_state_2014_2024.csv">saidi_by_state_2014_2024.csv</a>: every state, census division and the US total, 2014 to 2024, all five SAIDI series (columns <code>area, area_type, year, series, saidi_minutes</code>).</li>
<li><a href="data/reliability_metrics_2023_2024.csv">reliability_metrics_2023_2024.csv</a>: SAIDI, SAIFI and CAIDI with and without major events, plus the share of customers reported, for 2023 and 2024.</li>
<li><a href="data/summary.json">summary.json</a>: the figures this page is built from.</li>
</ul>
<p>The files and the script that builds this page are in the <a href="https://github.com/anchorape/us-power-outage-minutes">GitHub repository</a>. EIA data are in the public domain; this compilation is released under <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>.</p>

<h2>Turning outage hours into a backup plan</h2>
<p>An average hides the long outages that matter most for backup power, so look at your state's worst year as well as its 2024 figure. SolarGenReview's <a href="{SGR}/power-outage-tracker">US power outage tracker</a> covers the 2024 numbers state by state, the storms behind them, and backup sizing by outage risk. To turn hours without power into the battery capacity you need, its <a href="{SGR}/appliance-power-guide">appliance power guide</a> lists running and start-up watts for 47 household devices with a source for each, and <a href="{SGR}/articles/how-to-size-home-battery">how to size a home battery</a> walks through the arithmetic.</p>

<footer>
<p>Source: U.S. Energy Information Administration, Electric Power Annual, <a href="{T113}">Table 11.3</a> (reliability metrics by state, 2024 and 2023) and <a href="{T114}">Table 11.4</a> (SAIDI by state, 2014 to 2024), compiled from Form EIA-861. Retrieved October 12, 2026. Compiled by <a href="{SGR}">SolarGenReview</a>; not affiliated with EIA.</p>
</footer>
</main>
<script>
(function(){{var t=document.getElementById('t');var hs=t.tHead.rows[0].cells;var dir={{}};
for(var i=0;i<hs.length;i++){{(function(i){{if(hs[i].classList.contains('nosort'))return;hs[i].addEventListener('click',function(){{
var rows=Array.prototype.slice.call(t.tBodies[0].rows);dir[i]=!dir[i];var d=dir[i]?1:-1;
rows.sort(function(a,b){{var x=a.cells[i].getAttribute('data-v'),y=b.cells[i].getAttribute('data-v');var nx=parseFloat(x),ny=parseFloat(y);
if(!isNaN(nx)&&!isNaN(ny))return (nx-ny)*d;return x.localeCompare(y)*d;}});
rows.forEach(function(r){{t.tBodies[0].appendChild(r);}});
for(var j=0;j<hs.length;j++)if(!hs[j].classList.contains('nosort'))hs[j].setAttribute('aria-sort','none');
hs[i].setAttribute('aria-sort',d>0?'ascending':'descending');}});}})(i);}}}})();
</script>
</body>
</html>
"""
open(os.path.join(repo, "index.html"), "w", encoding="utf-8").write(page)

readme = f"""# US power outage minutes by state, 2014 to 2024

Average minutes without power per customer (SAIDI) for every US state, DC, the census divisions and the US total, 2014 to 2024, from the U.S. Energy Information Administration. Browse it at {URL}

In 2024 the average US customer went {fmt(any24)} minutes (about {h(any24)} hours) without power on EIA's "any method" series, the highest year since 2014; {fmt(wo24)} minutes without major event days.

## Files

| File | What it holds |
|---|---|
| `data/saidi_by_state_2014_2024.csv` | `area, area_type, year, series, saidi_minutes` for five series: `ieee_all_events`, `ieee_without_major_events`, `ieee_loss_of_supply_removed`, `any_method_all_events`, `any_method_without_major_events` |
| `data/reliability_metrics_2023_2024.csv` | SAIDI, SAIFI and CAIDI with and without major events, and the percent of customers reported, for 2023 and 2024 |
| `data/summary.json` | State summary used by the page (any-method series) |

Blank cells in EIA's tables (for example Hawaii in 2021 and 2022) are left out of the long file.

## Source

U.S. Energy Information Administration, Electric Power Annual: [Table 11.3]({T113}) and [Table 11.4]({T114}), compiled from Form EIA-861. Retrieved October 12, 2026. The script cross-checks the 2024 any-method SAIDI in Table 11.3 against Table 11.4 for every area.

## Licence

EIA data are in the public domain. This compilation is released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

Compiled by [SolarGenReview]({SGR}). For the 2024 figures with storm notes and backup sizing by outage risk, see its [US power outage tracker]({SGR}/power-outage-tracker).
"""
open(os.path.join(repo, "README.md"), "w", encoding="utf-8").write(readme)
print("ok", len(page), "over 24h:", over24h, "share major", share_major, "worst", worst24["state"], worst24["y2024"], "best", best24["state"], best24["y2024"])
