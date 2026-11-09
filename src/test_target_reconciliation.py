"""Missing fuel values stay missing and duplicate keys cannot silently aggregate."""
import csv
from reconcile_targets import ROOT, reconcile

with (ROOT / 'reports/energy_tidy.csv').open(newline='') as stream:
    rows = list(csv.DictReader(stream))
actual = reconcile(rows)
assert len(actual) == 55
assert actual[-1]['total_final_consumption_ktoe'] == 128091.8
assert abs(actual[-1]['electricity_plus_bioenergy_waste_ktoe'] - 30744.48) < 1e-8
probe = [dict(r) for r in rows]
for row in probe:
    if (row['year'], row['sector'], row['fuel']) == ('2024', 'All final users', 'Bioenergy & waste'):
        row.update(status='unavailable', consumption_ktoe='')
missing = reconcile(probe)[-1]
assert missing['electricity_plus_bioenergy_waste_ktoe'] is None
assert missing['complete_fuel_sum_minus_total_ktoe'] is None
try:
    reconcile(rows + [next(r for r in rows if r['sector'] == 'All final users')])
except ValueError:
    pass
else:
    raise AssertionError('Duplicate source key accepted')
print('Passed: 55 years, traced target values, missing-value and duplicate-key checks.')
