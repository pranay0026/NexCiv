import json
import os

notebook_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "notebooks", "training", "complaint_classifier.ipynb"))

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

updated = False
for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source_text = "".join(cell.get('source', []))
        if 'export_bundle = {' in source_text and "'priority_pipeline'" not in source_text:
            new_source_text = source_text.replace(
                "'prio_pipeline': prio_pipeline,",
                "'prio_pipeline': prio_pipeline,\n    'priority_pipeline': prio_pipeline,"
            )
            lines = [l + "\n" for l in new_source_text.splitlines(keepends=False)]
            cell['source'] = lines
            updated = True
            print("Successfully injected 'priority_pipeline' into notebook export cell.")

if updated:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Notebook updated and saved successfully!")
else:
    print("Notebook already up to date.")
