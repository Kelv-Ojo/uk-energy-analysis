"""Changing future consumption must not change earlier-origin predictions.

Perturbed values exist only in temporary test files, never published results.
"""
import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_probe(folder, perturb):
    (folder / 'forecasting').mkdir(parents=True)
    (folder / 'reports').mkdir()
    shutil.copyfile(ROOT / 'forecasting/backtest.py', folder / 'forecasting/backtest.py')
    with (ROOT / 'reports/sector_totals_ktoe.csv').open(newline='') as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames
        rows = list(reader)
    if perturb:
        for row in rows:
            if int(row['year']) >= 2020:
                row['All final users'] = str(float(row['All final users']) * 10)
    with (folder / 'reports/sector_totals_ktoe.csv').open('w', newline='') as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    subprocess.run([sys.executable, str(folder / 'forecasting/backtest.py')],
                   check=True, capture_output=True, text=True)
    with (folder / 'forecasting/backtest_predictions.csv').open(newline='') as saved:
        return {(r['model'], int(r['horizon']), int(r['origin_year'])):
                float(r['predicted_ktoe']) for r in csv.DictReader(saved)}


def main():
    with tempfile.TemporaryDirectory() as directory:
        normal = run_probe(Path(directory) / 'normal', False)
        changed = run_probe(Path(directory) / 'changed', True)
    assert normal.keys() == changed.keys()
    early = [key for key in normal if key[2] < 2020]
    assert len(early) == 162
    assert all(normal[key] == changed[key] for key in early), 'Future data changed an earlier forecast'
    for model in {key[0] for key in normal}:
        assert any(normal[k] != changed[k] for k in normal if k[0] == model and k[2] >= 2020), model
    print('Passed: 162 pre-2020 predictions unchanged; all three models respond after the perturbation.')


if __name__ == '__main__':
    main()
