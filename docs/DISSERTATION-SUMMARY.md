# MSc dissertation — UK energy consumption forecasting

My MSc dissertation, **Predicting UK Renewable and Non-Renewable Energy Consumption Using Machine Learning**, examined UK data for **1970–2024**, comparing **ARIMA, Random Forest and XGBoost**. The report used MAE, RMSE and MAPE and reported XGBoost as the strongest-performing model. Its original forecasting pipeline has not been reproduced here; numerical forecasts and model scores are withheld pending checks of units, target definitions and time-based evaluation.

## Problem and methodology

The research considered long-term UK consumption trends and forecasting. The report describes an ARIMA baseline and two tree-ensemble regressors using GDP, population, temperature and rainfall indicators. It describes model tuning and separate renewable/non-renewable targets. These are report-described methods, not experiments rerun in this repository.

## What the reported comparison means

The detailed test tables report lower MAE, RMSE and MAPE for XGBoost than Random Forest for both targets. The report attributes this to modelling nonlinear feature relationships and interactions. That is the report's interpretation, not an independently established explanation: unmatched validation designs prevent a reliable common-test comparison against ARIMA. No numerical scores, accuracy percentages or forecasts are reproduced here.

## What is independently reproducible here

The repository's Python and SQL analysis checks DESNZ Table C1 for 1970–2024, preserves source-cell references and uses original ktoe units. The historical results and charts below remain separate from the dissertation's modelling claims. See [historical findings](../reports/findings.md), [code](../src/analyze.py) and [reproduction instructions](../REPRODUCIBILITY.md).

## Verification boundaries

- The report's evaluation tables support MAE, RMSE and MAPE. R² was described by Kelvin but has not been independently confirmed in the reviewed text/tables; no R² claim or value is included.
- Detailed forecast tables cover 2025–2029; the stated research aim reaches 2030. No exact future horizon is advertised as verified output.
- Reported consumption conversions, electricity's inclusion in renewable grouping, ARIMA summary/table differences and plot/table alignment need original-code checks.
- Shuffled/random model evaluation and ARIMA's time-based setup are not a matched forecasting test. Model ranking is attributed to the report.
- LSTM/TFT appear as future work, not verified implementations.
- The recovered report has not been matched to an original submitted file in Aula. No forecasting notebook, split indices or saved predictions were found in the inspected repositories and local leads.

## Skills demonstrated

Research framing, energy-data interpretation, model comparison and critical review of validation choices. The accompanying reproducible historical analysis demonstrates Python, SQL, source tracing, unit checks and visual communication.

The complete dissertation, assessment material, identifiers and report figures are not included. Its copyright declaration requires institutional clarification before publishing substantive report extracts or recovered code. This original summary describes the work and its limits.
