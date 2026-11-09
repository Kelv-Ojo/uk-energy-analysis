# Historical chronological backtesting extension

This independent experiment uses verified Table C1 total final consumption for 1970–2024 in ktoe. It does not reproduce the MSc renewable/non-renewable targets, original experiments or future forecasts. Read [target reconciliation](../docs/TARGET-RECONCILIATION.md) and the [recovered notebook audit](../docs/RECOVERED-NOTEBOOK-AUDIT.md).

## Reproduce

Install forecasting/requirements.txt, then run:

```bash
python forecasting/backtest.py
python forecasting/check_results.py
python forecasting/error_bands.py
python forecasting/test_error_bands.py
python forecasting/test_no_lookahead.py
```

## Matched evaluation

Five fixed specifications share the same 22, 20 and 18 origin/target pairs at direct horizons 1, 3 and 5 years, starting with origin 2002. Every training label is observed by the forecast origin. The current origin annual observation is assumed available; this is not a forecast made before its release.

- Persistence predicts the origin consumption unchanged.
- Ridge uses an origin value and two lags, with scaling fitted within each origin.
- Random Forest uses the same lag features: 100 trees, depth 3, minimum leaf size 3, seed 42.
- XGBoost uses those lag features: 100 trees, depth 2, learning rate 0.05, squared-error objective, seed 42, one thread.
- ARIMA(1,1,0) without drift uses the observed series through each origin. Values are divided by 1,000 for numerical conditioning and predictions converted back to ktoe. Every fit must converge. Multi-step ARIMA forecasts and direct tree/regression forecasts use the same information cutoff and target years, although their modelling representations differ.

These specifications were fixed before running this extension; they are not an optimised comparison or the dissertation settings. No future GDP, population or weather observations are used. No model ranking from this experiment can validate a different target or evaluation design.

## Executed results, 9 November 2026

MAE in ktoe, rounded here; saved JSON and CSV retain precision. Positive skill means lower MAE than persistence at that horizon.

| Model | 1-year MAE | 3-year MAE | 5-year MAE |
| --- | ---: | ---: | ---: |
| Persistence | 3,915.30 | 6,137.68 | 9,411.21 |
| Ridge | 3,682.74 | 7,301.82 | 11,907.44 |
| Random forest | 4,671.27 | 8,835.83 | 12,416.15 |
| ARIMA(1,1,0) | 3,573.74 | 6,060.36 | 9,334.41 |
| XGBoost | 5,113.46 | 9,394.64 | 11,533.82 |

Fixed ARIMA has the lowest MAE and RMSE at all three horizons in this run. Its MAE improvement over persistence is about 8.7%, 1.3% and 0.8%; the longer-horizon differences are small. XGBoost does not beat persistence here. The dissertation-reported XGBoost ranking remains a separate, unvalidated finding for its original targets and splits.

All 300 predictions, cutoffs and actuals are in backtest_predictions.csv; backtest_metrics.json records 15 MAE/RMSE/skill summaries. check_results.py independently reconciles those summaries and confirms matched scopes. The expanded future-data isolation regression test changes consumption from 2020 onward in temporary copies: all 270 predictions originating before 2020 must stay identical, while every model must react at later origins. Temporary probes are discarded; no perturbed source or results are published.

## Limits and remaining validation

There are only 18–22 forecasts per horizon and multi-year errors overlap. No statistical significance or cross-horizon average is claimed. Hyperparameter tuning and structural-break sensitivity remain incomplete. No future forecast or guaranteed probability interval is published; random weather scenarios are not uncertainty intervals. The historical error-band diagnostic below is exploratory, not deployment calibration.

Historical source revisions are not a real-time vintage dataset, and publication delays are not modelled. Original exogenous snapshots and renewable-target reconstruction remain unresolved. This is an exploratory current-vintage total-consumption backtest, not a real-time deployment claim.

## Historical uncertainty diagnostic

error_bands.py forms symmetric error bands at a nominal 80% level from prior absolute errors for the same model and horizon. Only errors with target outcomes available by the current origin are eligible. It requires at least ten such errors and uses the ceiling of (n + 1) × 0.8 as an order-statistic rank. Bands are withheld earlier rather than using future outcomes. Overlapping errors and nonstationarity violate the exchangeability assumptions needed for a distribution-free coverage guarantee. These are historical diagnostics, not certified 80% prediction intervals.

The executed coverage is below. Each model has only 12, 8 and 4 evaluable bands at horizons 1, 3 and 5 respectively. Read counts alongside percentages.

| Model | 1-year coverage (12) | 3-year coverage (8) | 5-year coverage (4) |
| --- | ---: | ---: | ---: |
| Persistence | 91.7% | 62.5% | 75.0% |
| Ridge | 91.7% | 62.5% | 0.0% |
| Random forest | 83.3% | 50.0% | 50.0% |
| ARIMA(1,1,0) | 91.7% | 62.5% | 75.0% |
| XGBoost | 83.3% | 37.5% | 25.0% |

Longer-horizon undercoverage and the very small sample prevent a claim of reliable calibration. Historical error bands, calibration counts/cutoffs and median widths are saved separately. test_error_bands.py verifies future-outcome isolation and withholding with fewer than ten errors. No future scenarios are generated.
