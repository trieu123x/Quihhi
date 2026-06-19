import fitz
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")

print("--- Searching for Q27 ---")
for idx, page in enumerate(doc):
    text = page.get_text()
    if "27." in text:
        print(f"Page {idx} contains '27.':")
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
        for b in blocks:
            if "27." in b[4] or "26." in b[4] or "28." in b[4]:
                print(f"  [{round(b[1],1)}] {b[4].strip()!r}")

print("--- Searching for Q44 ---")
for idx, page in enumerate(doc):
    text = page.get_text()
    if "44." in text:
        print(f"Page {idx} contains '44.':")
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
        for b in blocks:
            if "44." in b[4] or "43." in b[4] or "45." in b[4]:
                print(f"  [{round(b[1],1)}] {b[4].strip()!r}")
