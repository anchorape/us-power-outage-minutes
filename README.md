# US power outage minutes by state, 2014 to 2024

Average minutes without power per customer (SAIDI) for every US state, DC, the census divisions and the US total, 2014 to 2024, from the U.S. Energy Information Administration. Browse it at https://anchorape.github.io/us-power-outage-minutes/

In 2024 the average US customer went 611.3 minutes (about 10.2 hours) without power on EIA's "any method" series, the highest year since 2014; 126.0 minutes without major event days.

## Files

| File | What it holds |
|---|---|
| `data/saidi_by_state_2014_2024.csv` | `area, area_type, year, series, saidi_minutes` for five series: `ieee_all_events`, `ieee_without_major_events`, `ieee_loss_of_supply_removed`, `any_method_all_events`, `any_method_without_major_events` |
| `data/reliability_metrics_2023_2024.csv` | SAIDI, SAIFI and CAIDI with and without major events, and the percent of customers reported, for 2023 and 2024 |
| `data/summary.json` | State summary used by the page (any-method series) |

Blank cells in EIA's tables (for example Hawaii in 2021 and 2022) are left out of the long file.

## Source

U.S. Energy Information Administration, Electric Power Annual: [Table 11.3](https://www.eia.gov/electricity/annual/table.php?t=epa_11_03.html) and [Table 11.4](https://www.eia.gov/electricity/annual/table.php?t=epa_11_04.html), compiled from Form EIA-861. Retrieved October 12, 2026. `scripts/build_eia.py` rebuilds the CSVs from the two table pages saved as `eia/11_03.html` and `eia/11_04.html`, and `scripts/build_page.py` renders the page. The build cross-checks the 2024 any-method SAIDI in Table 11.3 against Table 11.4 for every area.

## Licence

EIA data are in the public domain. This compilation is released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

Compiled by [SolarGenReview](https://www.solargenreview.com). For the 2024 figures with storm notes and backup sizing by outage risk, see its [US power outage tracker](https://www.solargenreview.com/power-outage-tracker).
