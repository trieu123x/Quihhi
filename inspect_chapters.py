import fitz
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")

chapters = []
for idx, page in enumerate(doc):
    text = page.get_text()
    matches = re.findall(r'(chương\s+\d+[:\s\n]*[^\n]*)', text, re.IGNORECASE)
    for m in matches:
        chapters.append((idx, m.strip()))

for idx, ch in chapters:
    print(f"Page {idx}: {ch}")
