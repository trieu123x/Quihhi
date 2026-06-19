import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")
page = doc[59]

print("--- Page 59 blocks ---")
blocks = page.get_text("blocks")
blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
for idx, b in enumerate(blocks):
    print(f"Block {idx} (y={round(b[1], 1)}, rect={b[:4]}): {b[4].strip()!r}")

print("\n--- Page 59 annotations ---")
for idx, annot in enumerate(page.annots()):
    print(f"Annot {idx} (rect={annot.rect}): {page.get_text('text', clip=annot.rect).strip()!r}")
