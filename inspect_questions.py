import fitz  # PyMuPDF
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")

# Print all text lines on page 1 with their block and line index
page = doc[1]
page_dict = page.get_text("dict")
for b_idx, block in enumerate(page_dict.get("blocks", [])):
    print(f"\nBlock {b_idx}:")
    for l_idx, line in enumerate(block.get("lines", [])):
        line_text = "".join(span["text"] for span in line.get("spans", []))
        print(f"  Line {l_idx}: {line_text!r}")
