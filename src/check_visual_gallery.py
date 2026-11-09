"""Check source references, catalogue coverage, exact image bytes and captions."""
import hashlib
import json
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
inventory = json.loads((ROOT / 'docs/dissertation-visual-inventory.json').read_text())
gallery = json.loads((ROOT / 'docs/gallery-manifest.json').read_text())
verified = json.loads((ROOT / 'docs/verified-visuals.json').read_text())
assert len(inventory['caption_inventory']) == 32
assert len(inventory['notebook_output_inventory']) == 29
assert len(inventory['original_figures']) == 49
assert len(verified) == 14 and len(gallery) == 63
assert len({r['id'] for r in gallery}) == 63
assert len([r for r in inventory['original_figures'] if r['source'] == 'MSc dissertation']) == 33
assert not ({r['relationship'] for r in inventory['excluded_media']} &
            {r.get('relationship') for r in inventory['original_figures']})
for entry in gallery + inventory['original_figures'] + inventory['notebook_output_inventory']:
    path = ROOT / entry['path']
    assert path.resolve().is_relative_to(ROOT.resolve())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], path
    with Image.open(path) as image:
        assert image.size == (entry['width'], entry['height'])
        image.verify()
for entry in inventory['original_figures']:
    assert 'not reproduced' in entry['status'].lower() or 'not rerun' in entry['status'].lower()
    assert entry['limitations']
    for reference in entry['notebook_outputs']:
        exact, = [r for r in inventory['notebook_output_inventory']
                  if (r['cell'], r['output']) == (reference['cell'], reference['output'])]
        assert exact['display_entry'] == entry['id']
for caption in inventory['caption_inventory']:
    assert caption['image_relationships'], caption
    assert all(rid in {r.get('relationship') for r in gallery} for rid in caption['image_relationships'])
document = (ROOT / 'docs/VISUAL-GALLERY.md').read_text(encoding='utf-8')
for target in re.findall(r'\]\((\.\./[^)]+\.png)\)', document):
    assert (ROOT / 'docs' / target).exists(), target
assert document.count('### ') == 63
assert not any((ROOT / 'assets/dissertation-gallery').rglob('*.docx'))
assert not any((ROOT / 'assets/dissertation-gallery').rglob('*.ipynb'))
print('Passed: 63 labelled figures, 32 caption references, 29 exact notebook outputs, hashes and image decoding.')
