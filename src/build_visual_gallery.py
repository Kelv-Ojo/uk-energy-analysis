"""Build source-checked charts; original dissertation images are never changed."""
import csv
import hashlib
import json
import math
import shutil
import statistics
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/dissertation-gallery/verified'
SECTORS = ['Industry', 'Transport', 'Domestic', 'Services']


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / 'data/manifest.json').read_text())
    for name, expected in manifest.items():
        assert hashlib.sha256((ROOT / 'data' / name).read_bytes()).hexdigest() == expected
    data = pd.read_csv(ROOT / 'reports/energy_tidy.csv')
    assert not data.duplicated(['year', 'sector', 'fuel']).any()
    # Independently trace every plotted historical value to the original workbook.
    workbook = openpyxl.load_workbook(ROOT / 'data/ECUK_2025_Consumption_tables.xlsx', read_only=True, data_only=True)
    source = list(workbook['Table C1'].iter_rows(max_row=61, max_col=57, values_only=True))
    for row in data.itertuples():
        column, line = openpyxl.utils.cell.coordinate_from_string(row.source_cell)
        value = source[line - 1][openpyxl.utils.column_index_from_string(column) - 1]
        if isinstance(value, (float, int)):
            assert row.consumption_ktoe == value or math.isclose(row.consumption_ktoe, value, rel_tol=1e-12)
        else:
            assert pd.isna(row.consumption_ktoe)
    workbook.close()
    totals = data[data.fuel.eq('Total')].pivot(index='year', columns='sector', values='consumption_ktoe')
    assert totals.index.tolist() == list(range(1970, 2025))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.titleweight': 'bold', 'axes.titlepad': 14, 'figure.facecolor': 'white'})
    figures = []
    chart_data = {}

    def save(slug, title, caption, fig, values, kind='Verified historical analysis'):
        fig.savefig(OUT / f'{slug}.png', dpi=170, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        figures.append({'id': slug, 'title': title, 'caption': caption, 'status': kind,
                        'path': f'assets/dissertation-gallery/verified/{slug}.png'})
        chart_data[slug] = values

    # Reuse the two already verified chart assets, without unnecessary recreation.
    for slug, filename, title in [('sector-trends', 'sector-trends.png', 'Final consumption by sector'),
                                  ('sector-changes', 'sector-changes.png', 'Sector changes from 1970 to 2024')]:
        shutil.copyfile(ROOT / 'assets/screenshots' / filename, OUT / f'{slug}.png')
        figures.append({'id': slug, 'title': title, 'caption': 'Existing source-checked historical chart, reused unchanged. Original ktoe converted to TWh where shown; no forecasting claim.',
                        'status': 'Verified historical analysis', 'path': f'assets/dissertation-gallery/verified/{slug}.png'})
    for sector in SECTORS:
        frame = data[data.sector.eq(sector) & ~data.fuel.eq('Total')].pivot(index='year', columns='fuel', values='consumption_ktoe')
        fig, ax = plt.subplots(figsize=(12, 6))
        (frame * .01163).plot(ax=ax, linewidth=1.8)
        ax.set(title=f'{sector}: final consumption by delivered fuel', xlabel='Year', ylabel='TWh')
        ax.legend(frameon=False, ncol=3, fontsize=9, loc='upper center', bbox_to_anchor=(.5, -.17))
        fig.tight_layout()
        save(f'{sector.lower()}-fuels', f'{sector} fuel breakdown',
             'Table C1 sector-specific fuel series, 1970–2024. Missing observations remain gaps. Delivered fuels are not a renewable/non-renewable classification; lines are not summed into a new total.',
             fig, json.loads(frame.to_json(orient='split')))
    fuel = data[data.sector.eq('All final users') & ~data.fuel.eq('Total')].pivot(index='year', columns='fuel', values='consumption_ktoe')
    fig, ax = plt.subplots(figsize=(12, 6))
    (fuel * .01163).plot(ax=ax, linewidth=1.8)
    ax.set(title='UK final consumption by delivered fuel', xlabel='Year', ylabel='TWh')
    ax.legend(frameon=False, ncol=3, fontsize=9, loc='upper center', bbox_to_anchor=(.5, -.17))
    fig.tight_layout()
    save('national-fuels', 'National fuel comparisons', 'All final users only; component sectors are not added again. Missing values remain gaps. The reported total has scope adjustments and need not equal the visible fuel sum.', fig, json.loads(fuel.to_json(orient='split')))
    fig, axes = plt.subplots(1, 3, figsize=(15, 7), sharey=True, sharex=True)
    labels = fuel.columns.tolist()
    for ax, year in zip(axes, [1970, 2000, 2024]):
        values = fuel.loc[year]
        positions = np.arange(len(values))
        ax.barh(positions, values * .01163, color='#176b87')
        for position, value in enumerate(values):
            if pd.isna(value):
                ax.text(0, position, 'Not available', va='center', fontsize=9)
        ax.set(title=str(year), xlabel='TWh', yticks=positions, yticklabels=labels)
    axes[0].invert_yaxis()
    fig.suptitle('Delivered fuel snapshots, not renewable shares', fontsize=16)
    fig.tight_layout()
    save('fuel-snapshots', 'Fuel snapshots in 1970, 2000 and 2024', 'Absolute consumption in TWh. Unavailable categories are explicitly labelled, not assigned zero. No pie normalisation conceals missing or out-of-scope fuel components.', fig, json.loads(fuel.loc[[1970, 2000, 2024]].to_json(orient='split')))
    yoy = totals[SECTORS].pct_change(fill_method=None).iloc[1:] * 100
    # Independent scalar calculation for every plotted percentage.
    for year in yoy.index:
        for sector in SECTORS:
            assert math.isclose(yoy.loc[year, sector], (totals.loc[year, sector] / totals.loc[year - 1, sector] - 1) * 100, abs_tol=1e-10)
    fig, ax = plt.subplots(figsize=(14, 4))
    limit = float(np.abs(yoy.to_numpy()).max())
    image = ax.imshow(yoy.T, aspect='auto', cmap='RdBu_r', vmin=-limit, vmax=limit)
    ticks = [i for i, year in enumerate(yoy.index) if year % 5 == 0 or year in [1971, 2024]]
    ax.set(title='Annual change in final consumption by sector', yticks=range(4), yticklabels=SECTORS,
           xticks=ticks, xticklabels=[str(yoy.index[i]) for i in ticks], xlabel='Year')
    fig.colorbar(image, ax=ax, label='Change from previous year (%)', pad=.02)
    fig.tight_layout()
    save('sector-yoy', 'Year-on-year sector changes', 'Changes calculated from reported sector totals, 1971–2024. A descriptive annual comparison; no attribution to weather, policy or efficiency is inferred.', fig, json.loads(yoy.to_json(orient='split')))
    corr = totals[SECTORS].corr()
    for a in SECTORS:
        for b in SECTORS:
            assert math.isclose(corr.loc[a, b], statistics.correlation(totals[a], totals[b]), abs_tol=1e-12)
    fig, ax = plt.subplots(figsize=(7, 6))
    image = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set(title='Correlation of annual sector totals', xticks=range(4), xticklabels=SECTORS, yticks=range(4), yticklabels=SECTORS)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center', va='center', color='white' if abs(corr.iloc[i, j]) > .55 else '#172238')
    fig.colorbar(image, ax=ax, label='Pearson correlation')
    fig.tight_layout()
    save('annual-sector-correlation', 'Annual sector correlation', '55 annual observations, 1970–2024. This is not the original notebook matrix, which correlated aggregated fuel profiles across sectors. Co-trending levels and autocorrelation limit interpretation; no causal claim.', fig, json.loads(corr.to_json(orient='split')))
    fig, ax = plt.subplots(figsize=(11, 5))
    (fuel[['Coal', 'Electricity', 'Petroleum']] * .01163).plot(ax=ax, linewidth=2)
    ax.set(title='Coal, electricity and petroleum in final consumption', xlabel='Year', ylabel='TWh')
    ax.legend(frameon=False)
    fig.tight_layout()
    save('major-fuels', 'Major fuel trajectories', 'National delivered-fuel categories from All final users. Unlike an all-sector sum, this does not count aggregate and component sectors together.', fig, json.loads(fuel[['Coal', 'Electricity', 'Petroleum']].to_json(orient='split')))
    predictions = pd.read_csv(ROOT / 'forecasting/backtest_predictions.csv')
    metrics = json.loads((ROOT / 'forecasting/backtest_metrics.json').read_text())
    names = ['Persistence', 'Ridge', 'Random forest', 'ARIMA(1,1,0)', 'XGBoost']
    assert len(predictions) == 300
    for row in predictions.itertuples():
        assert row.actual_ktoe == totals.loc[row.target_year, 'All final users']
        assert row.last_training_target_year <= row.origin_year
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    for ax, horizon in zip(axes, [1, 3, 5]):
        values = []
        for name in names:
            group = predictions[(predictions.model == name) & (predictions.horizon == horizon)]
            mae = float((group.predicted_ktoe - group.actual_ktoe).abs().mean())
            reported, = [r for r in metrics if r['model'] == name and r['horizon'] == horizon]
            assert math.isclose(mae, reported['mae_ktoe'], rel_tol=1e-10)
            values.append(mae)
        ax.bar(range(5), values, color=['#8d959c', '#b09055', '#5b8872', '#176b87', '#b65e42'])
        ax.set(title=f'{horizon}-year horizon', xticks=range(5), xticklabels=names)
        ax.tick_params(axis='x', rotation=60)
    axes[0].set_ylabel('MAE (ktoe), lower is better')
    fig.suptitle('Separate historical backtest on total final consumption', fontsize=15)
    fig.tight_layout()
    save('backtest-model-comparison', 'Matched chronological model comparison', 'New total-consumption experiment, not dissertation reproduction. The same 22/20/18 origin-target pairs are used at 1/3/5-year horizons. Fixed ARIMA has the lowest error here; no statistical significance is claimed.', fig, metrics, 'Verified separate historical backtest')
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True, sharey=True)
    for ax, name in zip(axes, ['ARIMA(1,1,0)', 'Random forest', 'XGBoost']):
        group = predictions[(predictions.model == name) & (predictions.horizon == 1)].sort_values('target_year')
        ax.plot(group.target_year, group.actual_ktoe, color='#434b53', label='Observed', linewidth=2)
        ax.plot(group.target_year, group.predicted_ktoe, color='#176b87', label='One-year prediction', linestyle='--')
        ax.set(title=name, ylabel='ktoe')
        ax.legend(frameon=False, ncol=2)
    axes[-1].set_xlabel('Target year')
    fig.suptitle('Actual versus one-year-ahead historical predictions', fontsize=16)
    fig.tight_layout()
    save('backtest-actual-predicted', 'Actual versus predicted on matched years', '22 one-year forecasts per model for target years 2003–2024. Current-vintage annual observations are assumed available at each origin. No future exogenous data or original dissertation target groups are used.', fig, json.loads(predictions[predictions.horizon.eq(1)].to_json(orient='records')), 'Verified separate historical backtest')
    bands = pd.read_csv(ROOT / 'forecasting/historical_error_bands.csv')
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    for ax, horizon in zip(axes, [1, 3, 5]):
        group = predictions[(predictions.model == 'ARIMA(1,1,0)') & predictions.horizon.eq(horizon)].sort_values('target_year')
        interval = bands[bands.model.eq('ARIMA(1,1,0)') & bands.horizon.eq(horizon)].sort_values('target_year')
        available = interval.dropna(subset=['lower_ktoe'])
        assert (available.last_calibration_target_year <= available.origin_year).all()
        ax.plot(group.target_year, group.actual_ktoe, color='#434b53', label='Observed')
        ax.plot(group.target_year, group.predicted_ktoe, color='#176b87', label='ARIMA forecast')
        ax.fill_between(interval.target_year, interval.lower_ktoe, interval.upper_ktoe, alpha=.2, color='#176b87', label='Exploratory prior-error band')
        ax.set(title=f'{horizon}-year horizon: {len(available)} evaluable bands', ylabel='ktoe')
        ax.legend(frameon=False, fontsize=9, ncol=3)
    axes[-1].set_xlabel('Historical target year')
    fig.suptitle('Historical error bands with origin-available residuals', fontsize=16)
    fig.tight_layout()
    save('historical-error-bands', 'Historical forecast uncertainty diagnostic', 'Nominal 80% prior-error bands, withheld until ten errors have matured. Only 12/8/4 bands per model are evaluable. Longer-horizon undercoverage and dependent errors prevent a calibrated 80% coverage claim; no future forecast is shown.', fig, json.loads(bands.to_json(orient='records')), 'Verified separate historical backtest; exploratory uncertainty')
    (ROOT / 'reports/gallery-chart-data.json').write_text(json.dumps(chart_data, indent=2, allow_nan=False) + '\n')
    (ROOT / 'docs/verified-visuals.json').write_text(json.dumps(figures, indent=2) + '\n')
    print(f'Validated source cells, annual changes, correlations and forecast metrics; built/reused {len(figures)} figures.')


if __name__ == '__main__':
    main()
