"""Trace candidate targets to published final-consumption cells, not generation."""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FUELS = {'Coal', 'Coke and breeze', 'Other solid fuels', 'Coke oven gas',
         'Town gas', 'Natural gas', 'Electricity', 'Heat', 'Bioenergy & waste', 'Petroleum'}


def reconcile(rows):
    final = {}
    for row in rows:
        if row['sector'] != 'All final users':
            continue
        key = (int(row['year']), row['fuel'])
        if key in final:
            raise ValueError(f'Duplicate target source key: {key}')
        final[key] = row
    output = []
    for year in range(1970, 2025):
        annual = {fuel: final[(year, fuel)] for fuel in FUELS | {'Total'}}
        values = {fuel: float(row['consumption_ktoe']) if row['status'] == 'reported' else None
                  for fuel, row in annual.items()}
        if any(v is not None and (not math.isfinite(v) or v < 0) for v in values.values()):
            raise ValueError('Invalid target source value')
        total = values['Total']
        assert total is not None
        missing = sorted(f for f in FUELS if values[f] is None)
        electricity, bio = values['Electricity'], values['Bioenergy & waste']
        diagnostic = electricity + bio if electricity is not None and bio is not None else None
        output.append({
            'year': year, 'total_final_consumption_ktoe': total,
            'electricity_ktoe': electricity, 'bioenergy_and_waste_ktoe': bio,
            'electricity_plus_bioenergy_waste_ktoe': diagnostic,
            'diagnostic_share_of_final_total_pct': diagnostic / total * 100 if diagnostic is not None else None,
            'complete_fuel_sum_minus_total_ktoe': sum(values[f] for f in FUELS) - total if not missing else None,
            'unavailable_fuels': '; '.join(missing),
            'total_source_cell': annual['Total']['source_cell'],
            'electricity_source_cell': annual['Electricity']['source_cell'],
            'bioenergy_waste_source_cell': annual['Bioenergy & waste']['source_cell'],
        })
    return output


if __name__ == '__main__':
    with (ROOT / 'reports/energy_tidy.csv').open(newline='') as stream:
        result = reconcile(csv.DictReader(stream))
    with (ROOT / 'reports/target_reconciliation.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=result[0])
        writer.writeheader()
        writer.writerows(result)
    summary = {'years': len(result), 'years_with_unavailable_fuels': sum(bool(r['unavailable_fuels']) for r in result),
               'latest_year': result[-1],
               'interpretation': 'Electricity plus bioenergy and waste is a diagnostic fuel grouping, not renewable consumption.'}
    (ROOT / 'reports/target_reconciliation.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
