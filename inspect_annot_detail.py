import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")
page = doc[3]

print(f"Page 3 has {len(list(page.annots()))} annotations:")
for idx, annot in enumerate(page.annots()):
    print(f"\nAnnot {idx}: type={annot.type}, rect={annot.rect}")
    # Print vertices if available
    # In PyMuPDF, vertices is a list of points (x, y) forming quads.
    # We can get the text that is actually covered by this annotation using the quads.
    # PyMuPDF has a built-in page.get_text("text", clip=...) or using vertices.
    # Let's see the text in annot.rect first
    print("Text in rect:", repr(page.get_text("text", clip=annot.rect).strip()))
    
    # Let's inspect page.get_text("words") to see which words intersect with this annot
    # words is a list of tuples: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
    words = page.get_text("words")
    intersecting_words = []
    for w in words:
        w_rect = fitz.Rect(w[:4])
        # Check intersection with annot.rect
        if annot.rect.contains(w_rect) or (annot.rect.intersects(w_rect) and (annot.rect & w_rect).get_area() / w_rect.get_area() > 0.5):
            intersecting_words.append(w[4])
    print("Intersecting words:", " ".join(intersecting_words))
