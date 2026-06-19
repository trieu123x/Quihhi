import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")

# Find where Q20 of Chapter 2 is
for idx, page in enumerate(doc):
    text = page.get_text()
    if "20." in text and "Chương 2" in text or (idx > 10 and idx < 25):
        # Let's check page 17 or 18
        if idx == 17:
            print(f"--- Page {idx} ---")
            blocks = page.get_text("blocks")
            blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
            for b in blocks:
                print(f"  [{round(b[1],1)}] {b[4].strip()!r}")
            for a_idx, annot in enumerate(page.annots()):
                print(f"  Annot {a_idx} (rect={annot.rect}): {page.get_text('text', clip=annot.rect).strip()!r}")
