"""Recover approved figure images without publishing the private source documents.

Usage: python src/recover_visuals.py --dissertation report.docx --notebook archive.zip
The allowlist excludes ethics, declarations, feedback and institutional branding.
"""
import argparse
import base64
import hashlib
import io
import json
import posixpath
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/dissertation-gallery'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
# Explicitly reviewed research visuals only. Do not expand to all embedded media.
DOC = {
14: ('Joined modelling data preview', 'method'),
16: ('Sector consumption trends', 'historical'),
17: ('Domestic fuel breakdown', 'historical'),
18: ('Industry fuel breakdown', 'historical'),
19: ('Services fuel breakdown', 'historical'),
20: ('Transport fuel breakdown', 'historical'),
21: ('National fuel consumption', 'historical'),
22: ('Fuel mix in 1970', 'historical'),
23: ('Fuel mix in 2000', 'historical'),
24: ('Fuel mix in 2024', 'historical'),
25: ('Year-on-year sector changes', 'historical'),
26: ('Correlation across aggregated fuel profiles', 'historical'),
27: ('Major fuel trends', 'historical'),
28: ('GDP and the two original target groups', 'features'),
29: ('Population and the two original target groups', 'features'),
30: ('Temperature and the two original target groups', 'features'),
31: ('Rainfall and the two original target groups', 'features'),
32: ('Original feature correlation matrix', 'features'),
33: ('ARIMA historical series and forecast bars', 'forecast'),
34: ('Random Forest historical and test predictions', 'model'),
35: ('Random Forest actual versus predicted', 'model'),
36: ('Random Forest feature importance', 'model'),
37: ('Original XGBoost pipeline diagram', 'method'),
38: ('XGBoost learning curves', 'model'),
39: ('XGBoost historical and test predictions', 'model'),
40: ('XGBoost actual versus predicted', 'model'),
41: ('XGBoost feature importance', 'model'),
42: ('Original target-group forecast comparison bars', 'forecast'),
43: ('Original second target-group forecast bars', 'forecast'),
44: ('Model forecast overlay in the dissertation body', 'forecast'),
69: ('Random Forest historical, test and future curves', 'forecast'),
70: ('XGBoost historical, test and future curves', 'forecast'),
71: ('ARIMA forecast image under the final comparison caption', 'forecast'),
}
NB = {
30: ('Sector consumption trends', 'historical'),
34: ('Sector fuel breakdown', 'historical'),
36: ('National fuel consumption', 'historical'),
40: ('Fuel mix snapshot', 'historical'),
46: ('Year-on-year sector changes', 'historical'),
49: ('Correlation across aggregated fuel profiles', 'historical'),
52: ('Major fuel trends', 'historical'),
67: ('Original two-target area chart', 'features'),
85: ('GDP or population scatter plots', 'features'),
86: ('Temperature scatter plots', 'features'),
87: ('Rainfall scatter plots', 'features'),
88: ('Original feature correlation matrix', 'features'),
99: ('ARIMA historical series and forecast bars', 'forecast'),
121: ('Random Forest historical and test predictions', 'model'),
123: ('Random Forest actual versus predicted', 'model'),
125: ('Random Forest feature importance', 'model'),
146: ('XGBoost historical and test predictions', 'model'),
148: ('XGBoost actual versus predicted', 'model'),
150: ('XGBoost feature importance', 'model'),
156: ('XGBoost learning curves', 'model'),
167: ('Model forecast overlay', 'forecast'),
169: ('Original target-group forecast comparison bars', 'forecast'),
170: ('Original second target-group forecast bars', 'forecast'),
}
LIMITS = {
'historical': 'Original figure, not reproduced. The notebook mislabels ktoe × 11,630 as kWh and some preparation fills missing cells with zero or merges fuel categories. See the separately validated charts for corrected units and scope.',
'features': 'Original figure, not reproduced. The Renewable label combines all electricity with bioenergy and waste; this is not measured renewable consumption. Original predictor indicator/vintage files are missing. Correlation is not causation.',
'model': 'Original saved result, not reproduced. Targets and absolute unit scale need correction; ARIMA and tree-model splits are not matched. Shuffled holdouts, tuning and predictor timing prevent an independently verified model ranking. Feature importance is model-specific association, not causal influence.',
'forecast': 'Original forecast illustration, not reproduced or validated. Original target definitions, unit scale and future predictor assumptions are unresolved. With observations through 2024, the five-year scenario is 2025–2029; it is not a verified 2030 forecast or a calibrated uncertainty interval.',
'method': 'Original research artefact, not a verified modelling dataset or successful reproduction. Original target labels and units remain disputed; original input snapshots are incomplete.',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pixel_key(raw):
    with Image.open(io.BytesIO(raw)) as im:
        return (im.size, digest(im.convert('RGB').tobytes()))


def save(raw, name):
    path = OUT / 'original' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    with Image.open(io.BytesIO(raw)) as im:
        width, height = im.size
        im.verify()
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(raw), 'width': width, 'height': height}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dissertation', type=Path, required=True)
    parser.add_argument('--notebook', type=Path, required=True)
    args = parser.parse_args()
    entries, captions, excluded = [], [], []
    pixels = {}
    with zipfile.ZipFile(args.dissertation) as archive:
        rels = {r.attrib['Id']: posixpath.normpath('word/' + r.attrib['Target'])
                for r in ET.fromstring(archive.read('word/_rels/document.xml.rels'))}
        root = ET.fromstring(archive.read('word/document.xml'))
        paragraphs = root.findall(f'.//{W}body/{W}p')
        uses = {}
        for index, paragraph in enumerate(paragraphs):
            for blip in paragraph.findall(f'.//{A}blip'):
                uses.setdefault(blip.attrib.get(R + 'embed'), []).append(index)
            text = ''.join(t.text or '' for t in paragraph.findall(f'.//{W}t'))
            if index >= 598 and text.startswith('Figure '):
                references = []
                for following in paragraphs[index:index + 4]:
                    following_text = ''.join(t.text or '' for t in following.findall(f'.//{W}t'))
                    if following is not paragraph and following_text.startswith('Figure '):
                        break
                    references += [b.attrib[R + 'embed'] for b in following.findall(f'.//{A}blip')]
                captions.append({'paragraph': index, 'caption': text.strip(), 'image_relationships': references})
        for number, (title, category) in DOC.items():
            rid = f'rId{number}'
            raw = archive.read(rels[rid])
            entry = {'id': f'doc-{number}', 'title': title, 'category': category,
                     'status': 'Original research figure; not reproduced', 'limitations': LIMITS[category],
                     'source': 'MSc dissertation', 'relationship': rid, 'paragraphs': uses.get(rid, []),
                     'captions': [c['caption'] for c in captions if rid in c['image_relationships']],
                     'notebook_outputs': [], **save(raw, f'dissertation-{number}.png')}
            entries.append(entry)
            pixels[pixel_key(raw)] = entry
        for rid, target in rels.items():
            if '/media/' in target and rid not in {f'rId{i}' for i in DOC}:
                excluded.append({'relationship': rid, 'reason': 'Non-gallery media: administrative/branding material or duplicate preview; not published.'})
    with zipfile.ZipFile(args.notebook) as archive:
        raw_notebook = archive.read('code_v3.ipynb')
        notebook = json.loads(raw_notebook)
    notebook_outputs = []
    for cell, block in enumerate(notebook['cells']):
        for output, saved in enumerate(block.get('outputs', [])):
            if 'image/png' not in saved.get('data', {}):
                continue
            raw = base64.b64decode(saved['data']['image/png'])
            key = pixel_key(raw)
            reference = {'cell': cell, 'output': output, 'sha256': digest(raw)}
            if key in pixels:
                entry = pixels[key]
                entry['notebook_outputs'].append(reference)
            else:
                title, category = NB[cell]
                entry = {'id': f'notebook-{cell}-{output}', 'title': title, 'category': category,
                         'status': 'Original saved notebook plot; not rerun', 'limitations': LIMITS[category],
                         'source': 'Recovered modelling notebook', 'notebook_outputs': [reference],
                         'captions': [], **save(raw, f'notebook-{cell}-{output}.png')}
                entries.append(entry)
                pixels[key] = entry
            # Preserve exact notebook bytes even where pixels match a report image.
            exact = ({k: entry[k] for k in ['path', 'sha256', 'width', 'height']}
                     if digest(raw) == entry['sha256'] else save(raw, f'notebook-source-{cell}-{output}.png'))
            notebook_outputs.append({**reference, **exact, 'display_entry': entry['id']})
    result = {
        'sources': {'dissertation_sha256': digest(args.dissertation.read_bytes()),
                    'notebook_sha256': digest(raw_notebook), 'notebook_cells': len(notebook['cells'])},
        'caption_inventory': captions, 'original_figures': entries, 'notebook_output_inventory': notebook_outputs,
        'excluded_media': excluded,
        'notes': [
            'Paragraph and notebook cell indices are zero-based; output indices include non-image outputs.',
            'The appendix has 32 captions, repeats number 31, and reuses images for paired scatter panels and ARIMA Figures 23/24.',
            'The final comparison caption points to an ARIMA-only image. The genuine multi-model overlay is a separate body image (doc-44).',
            'Identical decoded pixels share a display entry; exact notebook bytes are also preserved separately.',
            'Recovered images remain unchanged. Verification of image provenance does not verify the plotted results.',
        ],
    }
    (ROOT / 'docs/dissertation-visual-inventory.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'document_visuals': len(DOC), 'appendix_captions': len(captions),
                      'notebook_png_outputs': len(notebook_outputs), 'unique_display_entries': len(entries),
                      'excluded_media': len(excluded)}))


if __name__ == '__main__':
    main()
