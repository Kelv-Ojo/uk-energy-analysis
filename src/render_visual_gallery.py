"""Render the evidence catalogue for GitHub and an optional existing portfolio."""
import argparse
import hashlib
import html
import json
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GROUPS = [('historical', 'Original historical exploration'), ('features', 'Original feature exploration'),
          ('method', 'Original data and pipeline artefacts'), ('model', 'Original model diagnostics'),
          ('forecast', 'Original forecasting illustrations')]
ESC = html.escape


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portfolio', type=Path)
    args = parser.parse_args()
    inventory = json.loads((ROOT / 'docs/dissertation-visual-inventory.json').read_text())
    originals = inventory['original_figures']
    verified = json.loads((ROOT / 'docs/verified-visuals.json').read_text())
    all_entries = verified + originals
    for item in all_entries:
        path = ROOT / item['path']
        with Image.open(path) as image:
            item['width'], item['height'] = image.size
            image.verify()
        item['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT / 'docs/gallery-manifest.json').write_text(json.dumps(all_entries, indent=2) + '\n')
    lines = ['# MSc dissertation visual gallery', '',
             f'{len(verified)} source-checked figures and {len(originals)} distinct recovered display images. The document contains 32 appendix captions (including repeated numbering and shared panels), 33 approved body/appendix visual assets, and the notebook has 29 saved PNG outputs. Exact notebook bytes and source references are retained in the inventory.', '',
             '## How to read this gallery', '',
             '**Verified historical analysis** uses the fingerprinted ECUK 2025 source with corrected units and missing values preserved. **Verified separate historical backtest** uses a different total-consumption target and does not reproduce the dissertation. **Original research figure; not reproduced** is an unchanged recovered image: its presence verifies provenance, not model accuracy.', '',
             '[Machine-readable inventory](dissertation-visual-inventory.json) · [Chart data](../reports/gallery-chart-data.json) · [Target/unit audit](TARGET-RECONCILIATION.md) · [Notebook evaluation audit](RECOVERED-NOTEBOOK-AUDIT.md)', '',
             'Original charts retain their historical labels, including the disputed Renewable grouping and incorrect kWh scale. Read the caption on each image. No original forecast value, feature importance, model score or future scenario is promoted as independently validated. The full dissertation, ethics documents, declarations, feedback and institutional branding are not published.', '',
             '## Verified historical analysis and separate backtest', '']

    def markdown(item):
        provenance = ''
        if item.get('relationship'):
            provenance = f"Dissertation {item['relationship']}; paragraph(s) {', '.join(map(str, item['paragraphs']))}. "
        if item.get('notebook_outputs'):
            provenance += 'Notebook ' + ', '.join(f"cell {r['cell']}, output {r['output']}" for r in item['notebook_outputs']) + '. '
        return [f"### {item['title']}", '', f"**{item['status']}**", '',
                f"[![{item['title']}](../{item['path']})](../{item['path']})", '',
                item.get('caption', item.get('limitations', '')), '', provenance.strip(), '']

    for item in verified:
        lines += markdown(item)
    lines += ['## Recovered dissertation figures', '', 'Expand a subject to view its original figures. Click any image for full resolution.', '']
    for category, title in GROUPS:
        selected = [r for r in originals if r['category'] == category and r['source'] == 'MSc dissertation']
        lines += ['<details>', f'<summary>{title} ({len(selected)})</summary>', '']
        for item in selected:
            lines += markdown(item)
        lines += ['</details>', '']
    selected = [r for r in originals if r['source'] == 'Recovered modelling notebook']
    lines += ['<details>', f'<summary>Additional notebook plots and alternate renderings ({len(selected)})</summary>', '']
    for item in selected:
        lines += markdown(item)
    lines += ['</details>', '', '## Inventory and discrepancies', '',
              'The appendix repeats Figure 31. Figures 14/15, 16/17, 18/19 and 20/21 reuse two-panel scatter images. Figures 23/24 share one ARIMA image. The final caption says model comparison but references an ARIMA-only image; the actual multi-model overlay is recovered separately as doc-44. All 32 caption-to-image references are recorded without silently renumbering or correcting the originals.', '',
              'Notebook cell 49 correlates fuel profiles aggregated over years, not the annual sector totals used in the new verified correlation figure. Neither matrix proves causation. Original future-scenario plots and bars also have period/target limitations described in their captions.', '',
              '## Reproduction', '',
              '`python src/build_visual_gallery.py` traces plotted historical values to source workbook cells and checks annual changes, correlations and matched model errors. `python src/render_visual_gallery.py` regenerates this gallery. `python src/check_visual_gallery.py` verifies manifests and image integrity. Dependencies are in requirements-ci.txt; model fitting is not rerun by the gallery builder.', '',
              'To recover the originals again, supply private source paths to `python src/recover_visuals.py --dissertation <report.docx> --notebook <archive.zip>`. The original documents are deliberately not included. Inventory cell/paragraph/output indices are zero-based.', '']
    (ROOT / 'docs/VISUAL-GALLERY.md').write_text('\n'.join(lines), encoding='utf-8')
    if not args.portfolio:
        return
    portfolio = args.portfolio.resolve()
    assert (portfolio / 'energy.html').exists(), 'Use the existing portfolio checkout'
    target = portfolio / 'assets/dissertation-gallery'
    target.mkdir(parents=True, exist_ok=True)
    # Only copy displayed images; exact-byte duplicate source exports remain in the repo.
    for item in all_entries:
        destination = portfolio / item['path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / item['path'], destination)

    def figure(item):
        status = item['status']
        caption = item.get('caption', item.get('limitations', ''))
        provenance = ''
        if item.get('relationship'):
            provenance = f"Dissertation {item['relationship']}. "
        if item.get('notebook_outputs'):
            provenance += 'Notebook ' + ', '.join(f"cell {o['cell']}, output {o['output']}" for o in item['notebook_outputs']) + '. '
        return f'''<figure class="visual-entry" id="visual-{item['id']}"><h3>{ESC(item['title'])}</h3><p class="visual-status">{ESC(status)}</p><a href="{item['path']}" target="_blank" rel="noopener" aria-label="Open full-size {ESC(item['title'])}; {ESC(status)}"><img src="{item['path']}" alt="{ESC(item['title'])}. {ESC(status)}." width="{item['width']}" height="{item['height']}" loading="lazy" decoding="async"/></a><figcaption>{ESC(caption)} <span class="visual-provenance">{ESC(provenance)}</span><a href="{item['path']}" target="_blank" rel="noopener">Open full-size image ↗</a></figcaption></figure>'''

    content = [f'''<!-- ENERGY-GALLERY-START --><section class="energy-gallery" id="visual-gallery" aria-labelledby="gallery-title"><h2 id="gallery-title">Dissertation visual gallery</h2><p class="gallery-intro">{len(verified)} source-checked charts and {len(originals)} recovered original visuals show the breadth of the research. Each caption identifies what has been verified.</p><nav class="gallery-navigation" aria-label="Visual gallery sections"><a href="#verified-history">Verified history</a><a href="#verified-backtest">Separate backtest</a><a href="#original-research">Original dissertation figures</a><a href="https://github.com/Kelv-Ojo/uk-energy-analysis/blob/main/docs/VISUAL-GALLERY.md">Full inventory and sources ↗</a></nav><h2 id="verified-history">Verified historical analysis</h2><p>Rebuilt from the documented 1970–2024 ECUK snapshot with corrected units and missing values preserved.</p><div class="visual-grid">''']
    content += [figure(r) for r in verified if r['status'] == 'Verified historical analysis']
    content += ['</div><h2 id="verified-backtest">Separate historical backtest</h2><p>New chronological experiments on total final consumption. These do not reproduce the dissertation’s original target groups or validate its model ranking.</p><div class="visual-grid">']
    content += [figure(r) for r in verified if r['status'] != 'Verified historical analysis']
    content += ['</div><h2 id="original-research">Original dissertation figures</h2><p class="gallery-caveat">Recovered images are unchanged and have not been reproduced. Original kWh labels have a scale error, the Renewable grouping is disputed, and original model splits and predictor timing remain unresolved. View these as research artefacts, not validated numerical results or future forecasts.</p><p>Expand a subject below. Full-resolution images open separately; the original report and private university material remain unpublished.</p>']
    for category, title in GROUPS:
        selected = [r for r in originals if r['category'] == category and r['source'] == 'MSc dissertation']
        content += [f'<details class="gallery-archive"><summary>{title} ({len(selected)})</summary><div class="visual-grid visual-grid--archive">']
        content += [figure(r) for r in selected]
        content += ['</div></details>']
    selected = [r for r in originals if r['source'] == 'Recovered modelling notebook']
    content += [f'<details class="gallery-archive"><summary>Additional notebook plots and alternate renderings ({len(selected)})</summary><div class="visual-grid visual-grid--archive">']
    content += [figure(r) for r in selected]
    content += ['</div></details><p class="gallery-source-note">The source appendix repeats figure numbering and reuses some images. The final comparison caption references an ARIMA-only figure; the genuine multi-model overlay is shown separately. <a href="https://github.com/Kelv-Ojo/uk-energy-analysis/blob/main/docs/dissertation-visual-inventory.json">Inspect the exact caption and notebook mappings ↗</a>.</p></section><!-- ENERGY-GALLERY-END -->']
    page = portfolio / 'energy.html'
    text = page.read_text(encoding='utf-8')
    text = text.replace('Descriptive historical analysis of a fixed workbook release. It is not a forecast, causal study or emissions inventory. Electricity cannot be labelled renewable from this table.',
                        'The verified historical analysis describes a fixed workbook release; it is not a causal study or emissions inventory. Electricity cannot be labelled renewable from this table. The separate backtest and recovered original research figures are identified individually in the gallery below.')
    if '<!-- ENERGY-GALLERY-START -->' in text:
        before, rest = text.split('<!-- ENERGY-GALLERY-START -->', 1)
        _, after = rest.split('<!-- ENERGY-GALLERY-END -->', 1)
        text = before + '\n'.join(content) + after
    else:
        text = text.replace('</main>', '\n'.join(content) + '</main>')
    if 'energy-gallery.css' not in text:
        text = text.replace('</head>', '<link rel="stylesheet" href="energy-gallery.css?v=20261109"/></head>')
    text = text.replace('<p><a class="button" href="explore.html#energy">Explore the data</a></p>', '<p><a class="button" href="explore.html#energy">Explore the data</a> <a class="gallery-jump" href="#visual-gallery">View dissertation visual gallery ↓</a></p>')
    page.write_text(text, encoding='utf-8')
    (target / 'manifest.json').write_text(json.dumps(all_entries, indent=2) + '\n')
    print(f'Rendered {len(all_entries)} gallery figures for the existing portfolio.')


if __name__ == '__main__':
    main()
