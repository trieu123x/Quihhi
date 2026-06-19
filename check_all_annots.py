import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")

for page_idx in range(len(doc)):
    page = doc[page_idx]
    annots = list(page.annots())
    if not annots:
        continue
    print(f"\nPage {page_idx} annotations ({len(annots)}):")
    for idx, annot in enumerate(annots):
        text = page.get_text("text", clip=annot.rect).strip()
        # count lines
        lines = text.split('\n')
        if len(lines) > 2:
            print(f"  Annot {idx} has {len(lines)} lines! Text snippet: {text[:100]!r}")
        else:
            print(f"  Annot {idx}: {text!r}")
