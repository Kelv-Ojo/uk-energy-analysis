# Recovered modelling notebook audit

Reviewed 8 November 2026. The original notebook archive has now been recovered privately from the author's email. It contains one notebook and no input datasets. It has not been rerun or published, and its saved outputs are not fresh validation evidence. The complete dissertation and restricted material remain excluded.

Notebook SHA-256: `c679f3459c6ac543f3539507856f2daa3abe5c8bca8b588f7de6152ac3832ce9` (178 cells; cell references below are zero-based).

## Findings verified directly in code

- Cell 16 multiplies source consumption by 11,630 and labels the result kWh. The source Table C1 is in ktoe, so conversion to kWh also requires the thousands factor. Existing repository historical results retain ktoe or correctly convert to TWh; notebook absolute scores must not be copied as corrected results.
- Cell 64 groups Bioenergy & Waste and all Electricity into a variable named Renewable. Final electricity consumption does not identify renewable generation. This target cannot be described as measured renewable consumption without an appropriate generation/source attribution method. Heat and other categories also need definition review.
- Cell 92 fits a StandardScaler on all years before cell 94's last-five-year split. This learns future feature distributions. Later tree-model branches use separate data; this finding should not be misrepresented as evidence that every fitted model uses that scaler.
- ARIMA uses the last five years for testing (cells 94, 102–103). Random Forest and XGBoost instead use shuffled ten-row tests (cells 108 and 130). These are not matched chronological forecast evaluations.
- Cell 115 applies cross-validation to the Random Forest test partition itself. Those scores are refitted small-sample CV results, not the original untouched holdout predictions.
- GDP, population and annual weather features refer to the target year. Their realised values are unavailable for an advance forecast unless forecast separately using information available at the origin. Shuffled KFold tuning also allows later years into earlier validation folds.
- Future predictor generation adds unseeded random weather noise (cell 159). Cell 160 sets a five-year horizon following the final observed year. With data through 2024, that is 2025–2029, not a validated 2030 projection. Scenarios are not forecast uncertainty intervals.
- The archive references local ECUK, GDP and population files and live Met Office series. The original GDP/population snapshots are not included. Matching their indicator definitions, vintages and coverage remains necessary before an exact reproduction.

## Portfolio decision

Retain XGBoost's ranking only as a dissertation-reported finding. Do not publish original exact scores or future estimates as independently validated. Keep the new consumption-only chronological experiment separate: it answers a different target question using a verified source series, with no future exogenous observations. Recover the remaining inputs and resolve target definitions before rebuilding the dissertation comparison. Historical revisions, publication delays, small samples and uncertainty remain limitations.
