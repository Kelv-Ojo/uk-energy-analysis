"""Later outcomes must not influence an earlier historical error band."""
import csv
from error_bands import ROOT, build_bands

with (ROOT / 'backtest_predictions.csv').open(newline='') as stream:
    rows = list(csv.DictReader(stream))
normal = build_bands(rows)
changed = [dict(r) for r in rows]
for row in changed:
    if int(row['target_year']) >= 2020:
        row['actual_ktoe'] = str(float(row['actual_ktoe']) * 10)
probe = build_bands(changed)
assert len(normal) == 300
for before, after in zip(normal, probe):
    if int(before['origin_year']) < 2020:
        for key in ['lower_ktoe', 'upper_ktoe', 'calibration_errors', 'last_calibration_target_year']:
            assert before[key] == after[key], (before, key)
    if before['last_calibration_target_year'] != '':
        assert before['last_calibration_target_year'] <= int(before['origin_year'])
    if before['calibration_errors'] < 10:
        assert before['lower_ktoe'] == before['upper_ktoe'] == before['covered'] == ''
    else:
        assert before['lower_ktoe'] <= before['upper_ktoe']
        assert before['covered'] in (0, 1)
assert any(r['covered'] != '' for r in normal)
assert any(a['lower_ktoe'] != b['lower_ktoe'] for a, b in zip(normal, probe) if int(a['origin_year']) >= 2020)
print('Passed: historical error-band cutoff, future-outcome isolation and small-sample withholding.')
