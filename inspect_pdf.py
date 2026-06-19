import fitz  # PyMuPDF
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")
page = doc[1]
annots = list(page.annots())

print(f"Page 1 has {len(annots)} annotations:")
for i, annot in enumerate(annots):
    print(f"--- Annot {i} ---")
    print("Rect:", annot.rect)
    # Extract text from the annot rect
    # Try different methods or check coordinates
    text = page.get_text("text", clip=annot.rect)
    print("Text (clip):", repr(text.strip()))
    
    # Let's inspect the span level elements overlapping with the annot.rect
    overlapping_spans = []
    page_dict = page.get_text("dict")
    for block in page_dict.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                # Check if span bbox intersects with annot rect
                s_bbox = fitz.Rect(span["bbox"])
                if annot.rect.intersects(s_bbox):
                    overlapping_spans.append(span["text"])
    print("Overlapping spans:", overlapping_spans)
