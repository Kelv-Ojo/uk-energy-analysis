"""Independently reconcile saved metrics and matched evaluation scopes."""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
with (ROOT.parent / 'reports/sector_totals_ktoe.csv').open(newline='') as stream:
    source_actual = {int(r['year']): float(r['All final users']) for r in csv.DictReader(stream)}
rows = list(csv.DictReader((ROOT / 'backtest_predictions.csv').open(newline='')))
metrics = json.loads((ROOT / 'backtest_metrics.json').read_text())
models = {'Persistence', 'Ridge', 'Random forest', 'ARIMA(1,1,0)', 'XGBoost'}
assert {r['model'] for r in rows} == models
assert len(rows) == 300 and len(metrics) == 15
keys = [(r['model'], r['origin_year'], r['horizon']) for r in rows]
assert len(set(keys)) == len(keys)
for horizon, count in [(1, 22), (3, 20), (5, 18)]:
    groups = {model: [r for r in rows if int(r['horizon']) == horizon and r['model'] == model] for model in models}
    scopes = [{(r['origin_year'], r['target_year'], r['actual_ktoe']) for r in group} for group in groups.values()]
    assert all(scope == scopes[0] and len(scope) == count for scope in scopes)
    for row in [r for group in groups.values() for r in group]:
        assert int(row['target_year']) - int(row['origin_year']) == horizon
        assert int(row['last_training_target_year']) <= int(row['origin_year'])
        assert math.isfinite(float(row['predicted_ktoe']))
        assert float(row['actual_ktoe']) == source_actual[int(row['target_year'])]
        if row['model'] == 'Persistence':
            assert float(row['predicted_ktoe']) == source_actual[int(row['origin_year'])]
    naive_mae = sum(abs(float(r['predicted_ktoe']) - float(r['actual_ktoe'])) for r in groups['Persistence']) / count
    for model, group in groups.items():
        errors = [float(r['predicted_ktoe']) - float(r['actual_ktoe']) for r in group]
        metric, = [m for m in metrics if m['model'] == model and m['horizon'] == horizon]
        assert metric['origins'] == count
        mae = sum(map(abs, errors)) / count
        rmse = math.sqrt(sum(e * e for e in errors) / count)
        for name, expected in [('mae_ktoe', mae), ('rmse_ktoe', rmse), ('mae_skill_vs_persistence', 1 - mae / naive_mae)]:
            assert math.isclose(metric[name], expected, rel_tol=1e-10, abs_tol=1e-8), (model, horizon, name)
print('Passed: 300 matched forecasts, training cutoffs and all 15 error/skill summaries.')
