import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")

# Page 2 contains Q9
page = doc[2]
print("--- Page 2 blocks ---")
blocks = page.get_text("blocks")
blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
for idx, b in enumerate(blocks):
    print(f"Block {idx} (y={round(b[1], 1)}, rect={b[:4]}): {b[4].strip()!r}")

print("\n--- Page 2 annotations ---")
for idx, annot in enumerate(page.annots()):
    text = page.get_text("text", clip=annot.rect).strip()
    print(f"Annot {idx} (rect={annot.rect}): {text!r}")
    
# Let's inspect page 3 blocks around the top (where the options of Q9 continue)
print("\n--- Page 3 top blocks ---")
page3 = doc[3]
blocks3 = page3.get_text("blocks")
blocks3 = sorted(blocks3, key=lambda b: (b[1], b[0]))
for idx, b in enumerate(blocks3[:10]):
    print(f"Block {idx} (y={round(b[1], 1)}, rect={b[:4]}): {b[4].strip()!r}")

print("\n--- Page 3 annotations ---")
for idx, annot in enumerate(page3.annots()):
    text = page3.get_text("text", clip=annot.rect).strip()
    print(f"Annot {idx} (rect={annot.rect}): {text!r}")
