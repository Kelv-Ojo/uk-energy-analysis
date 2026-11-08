"""Check saved backtest scope, temporal cutoffs and independently recomputed errors."""
import csv
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parents[1]
with (root / 'reports/sector_totals_ktoe.csv').open() as f:
    actual = {int(r['year']): float(r['All final users']) for r in csv.DictReader(f)}
with (root / 'forecasting/backtest_predictions.csv').open() as f:
    rows = list(csv.DictReader(f))
metrics = json.loads((root / 'forecasting/backtest_metrics.json').read_text())
assert len(rows) == 180 and len(metrics) == 9
keys = {(r['model'], int(r['horizon']), int(r['origin_year'])) for r in rows}
assert len(keys) == len(rows)
for row in rows:
    origin, target, horizon = map(int, (row['origin_year'], row['target_year'], row['horizon']))
    assert target == origin + horizon
    assert int(row['last_training_target_year']) <= origin
    assert float(row['actual_ktoe']) == actual[target]
    assert math.isfinite(float(row['predicted_ktoe']))
    if row['model'] == 'Persistence':
        assert float(row['predicted_ktoe']) == actual[origin]
for metric in metrics:
    selected = [r for r in rows if r['model'] == metric['model'] and int(r['horizon']) == metric['horizon']]
    assert len(selected) == metric['origins']
    errors = [float(r['predicted_ktoe']) - float(r['actual_ktoe']) for r in selected]
    assert math.isclose(sum(abs(e) for e in errors) / len(errors), metric['mae_ktoe'], rel_tol=1e-10)
    assert math.isclose(math.sqrt(sum(e*e for e in errors) / len(errors)), metric['rmse_ktoe'], rel_tol=1e-10)
print('Verified 180 predictions, temporal cutoffs, persistence baseline and nine error summaries.')
