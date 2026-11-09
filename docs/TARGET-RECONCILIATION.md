# Target and predictor reconciliation

Verified 9 November 2026 against the fingerprinted ECUK 2025 workbook and the privately recovered notebook. This resolves the target used by the **new historical experiment**; it does not reconstruct a valid renewable/non-renewable dissertation target.

## Target decision

Use Table C1, sector `All final users`, fuel `Total`, 1970–2024, in **ktoe**. Keep the reported total rather than rebuilding it from visible fuel columns. One ktoe is 0.01163 TWh or 11,630,000 kWh. The notebook's factor of 11,630 produces MWh from ktoe, despite its kWh label.

Notebook cell 64 adds electricity to bioenergy and waste and calls the result Renewable. In 2024 these source cells are BA61 = 23,418.37 and BC61 = 7,326.11 ktoe; their sum is **30,744.48 ktoe**, or **24.002% of the reported final total**. That is a diagnostic grouping, **not a renewable share**. Electricity includes multiple generation sources; bioenergy and waste is a combined category. Do not treat either category as a complete classification by renewable origin.

`python src/reconcile_targets.py` produces a 55-year, source-cell-traced diagnostic in reports/target_reconciliation.csv. Missing components remain missing: 29 years have unavailable fuel cells. Unlike the notebook's pivot/fillna and sum, this diagnostic does not turn unavailable observations into zero. `python src/test_target_reconciliation.py` checks the traced endpoint, duplicate keys and missing-value handling.

## Why visible fuel sums differ from the total

In 2024 the visible fuel sum is 22.7633 ktoe below the reported total. This is a **fuel-column** diagnostic, separate from the existing small **sector-total** rounding check. Do not call this fuel difference rounding or force the fuel sum to equal the total.

Table C1's total header explicitly references Notes 2 and 6. In the workbook Notes sheet, Note 2 describes changing treatment of blast furnace gas and inclusion in the total from 1996, and earlier inclusion of creosote and pitch; Note 6 excludes non-energy uses. These scope notes explain why a simple visible-column reconstruction is not a safe substitute for the published total. This audit has not independently decomposed every annual residual into its individual balance items.

## Original predictor investigation

| Input in recovered code | Established | Still required for exact reproduction |
| --- | --- | --- |
| gdp_data.csv | World Bank-style CSV, three skipped metadata rows, UK filter, years 1970–2024, then a Year/GDP reshape (cells 70–72) | Indicator code, price basis, currency, download date, release vintage and original file hash |
| population_Data.csv | Same UK/year reshape (cells 73–75) | Indicator code, coverage, vintage and original hash |
| Met Office UK Tmean/date/UK.txt | Annual mean temperature selected (cell 78) | The exact downloaded vintage, units/header and availability dates |
| Met Office UK Rainfall/date/UK.txt | Annual rainfall selected (cell 79) | Exact vintage, header/units and availability dates |

The code does not select a GDP indicator code before discarding metadata. A file containing several UK indicators could create duplicate years and multiply joined rows. Any recovered inputs must pass unique-year, exact coverage, missingness, indicator and many-to-one merge checks before fitting. Do not infer GDP units from the generic filename or the magnitude of saved values. For example, [World Bank NY.GDP.MKTP.CD](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/NY.GDP.MKTP.CD/~/~/~/home) specifically means GDP at current prices in US dollars; the notebook does not establish that this was its chosen series.

Current public downloads would be new snapshots, not recovered originals. Realised target-year GDP, population and weather also remain unavailable at an earlier forecast origin. Use lagged released observations or separately origin-available forecasts, never realised future values. The new consumption-only experiment deliberately requires none of these missing exogenous files. Its current-vintage and annual-release assumptions remain explicit in forecasting/README.md.

[Official ECUK 2025 publication](https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025). Source attribution and workbook hash are retained in the existing repository manifest. No original dissertation, notebook or private correspondence is republished.
