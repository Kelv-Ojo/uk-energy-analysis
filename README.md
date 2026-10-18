# UK Energy Consumption Analysis

**Question:** How has UK final energy consumption changed across sectors between 1970 and 2024, and where should further demand analysis focus?

An analysis of the DESNZ Energy Consumption in the UK 2025 workbook, developed from my existing energy project with assisted code and documentation improvements. It demonstrates source inspection, reproducible cleaning, SQL comparisons, unit validation and communication of findings.

## Findings

- Total final consumption fell **12.3%** between 1970 and 2024.
- Consumption increased **2.6%** from 2023 to 2024.
- Transport represented **42.2%** of final consumption in 2024, making it a useful focus for further demand research.

![Energy trends by sector](reports/sector_trends.png)

![Long-term sector changes](reports/sector_changes.png)

## Reproduce

From this repository's root, using Python 3.10 or later:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/analyze.py
```

Windows: activate with `.venv\Scripts\activate`. The source workbook is included; no API key or external service is needed. Outputs are regenerated in `reports/`.

## Analytical decisions

- Read only the relevant area of Table C1, rather than the workbook's inflated formatted range.
- Retain source cell references, missing-value status and original ktoe units in the tidy dataset.
- Correct unit conversion: **1 ktoe = 0.01163 TWh**. The earlier notebook omitted the thousands factor when converting to kWh.
- Use reported totals for comparisons. Never sum the aggregate `All final users` with individual sectors.
- Preserve missing fuel values, including `[x]`, rather than assuming zero.
- Validate 55 consecutive years, unique keys, complete totals, nonnegative values and sector reconciliation. Published rounding causes at most a 2 ktoe sector-sum difference.

## Explore the work

- [Analysis code](src/analyze.py)
- [SQL endpoint comparison](sql/sector_changes.sql)
- [Findings and limitations](reports/findings.md)
- [Tidy dataset with source cells](reports/energy_tidy.csv)
- [Computed metrics](reports/metrics.json)
- [Input SHA-256 fingerprint](data/manifest.json)

## Source and limits

[DESNZ: Energy consumption in the UK 2025](https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025), Table C1, 1970–2024. The included local workbook snapshot is fingerprinted in the manifest; this is not a claim to use the newest release. Government data is attributed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

These are descriptive comparisons, not causal estimates or forecasts. Weather, economic activity and efficiency could explain changes but are not measured here. Electricity consumption does not identify renewable generation. This project does not claim emissions reductions, client work or commercial impact.
