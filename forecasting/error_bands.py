"""Exploratory historical error bands; no exchangeability/coverage guarantee."""
import csv
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEVEL = 0.8
MIN_ERRORS = 10


def build_bands(rows):
    bands = []
    for row in rows:
        origin = int(row['origin_year'])
        eligible = [r for r in rows if r['model'] == row['model']
                    and r['horizon'] == row['horizon'] and int(r['target_year']) <= origin]
        errors = sorted(abs(float(r['predicted_ktoe']) - float(r['actual_ktoe'])) for r in eligible)
        result = {key: row[key] for key in ['model', 'horizon', 'origin_year', 'target_year']}
        result.update(calibration_errors=len(errors), last_calibration_target_year=max((int(r['target_year']) for r in eligible), default=''),
                      lower_ktoe='', upper_ktoe='', covered='')
        if len(errors) >= MIN_ERRORS:
            # Finite-sample rank, but overlapping nonstationary errors are not exchangeable.
            rank = math.ceil((len(errors) + 1) * LEVEL)
            assert rank <= len(errors)
            radius = errors[rank - 1]
            prediction, actual = float(row['predicted_ktoe']), float(row['actual_ktoe'])
            result.update(lower_ktoe=prediction - radius, upper_ktoe=prediction + radius,
                          covered=int(abs(actual - prediction) <= radius))
        bands.append(result)
    return bands


if __name__ == '__main__':
    with (ROOT / 'backtest_predictions.csv').open(newline='') as stream:
        bands = build_bands(list(csv.DictReader(stream)))
    with (ROOT / 'historical_error_bands.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=bands[0])
        writer.writeheader()
        writer.writerows(bands)
    summary = []
    for model in sorted({r['model'] for r in bands}):
        for horizon in ['1', '3', '5']:
            available = [r for r in bands if r['model'] == model and r['horizon'] == horizon and r['covered'] != '']
            summary.append({'model': model, 'horizon': int(horizon), 'nominal_level': LEVEL,
                            'evaluated_bands': len(available),
                            'observed_coverage': statistics.mean(r['covered'] for r in available) if available else None,
                            'median_width_ktoe': statistics.median(r['upper_ktoe'] - r['lower_ktoe'] for r in available) if available else None})
    (ROOT / 'error_band_metrics.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
