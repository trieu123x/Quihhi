import fitz  # PyMuPDF
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

WATERMARKS = [
    "downloaded by",
    "lomarcpsd",
    "studocu is not sponsored",
    "scan to open on studocu",
    "câu hỏi ôn tập csattt",
    "thực tập cơ sở (học viện",
    "học viện công nghệ bưu chính viễn thông"
]

def is_watermark(text):
    t = text.lower().strip()
    # Check if watermark pattern
    if not t:
        return True
    # lOMoARcPSD watermark
    if "lomoarcpsd" in t:
        return True
    for w in WATERMARKS:
        if w in t:
            return True
    return False

doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")

# We want to extract questions
# Let's inspect pages 1 to 5 to see what we extract
for page_idx in range(1, 6):
    page = doc[page_idx]
    annots = list(page.annots())
    print(f"\n================ PAGE {page_idx} ================")
    print(f"Annotations: {len(annots)}")
    
    # Get all text blocks
    blocks = page.get_text("blocks")
    # Sort blocks by y coordinate, then x coordinate
    blocks = sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))
    
    for b in blocks:
        x0, y0, x1, y1, text, block_no, block_type = b
        text_clean = text.strip()
        if is_watermark(text_clean):
            continue
            
        # Check if highlighted
        block_rect = fitz.Rect(x0, y0, x1, y1)
        is_highlighted = False
        highlight_intersect_text = ""
        for annot in annots:
            if annot.rect.intersects(block_rect):
                # Check area of intersection
                intersect = annot.rect & block_rect
                if intersect.get_area() > 10:  # arbitrary threshold
                    is_highlighted = True
                    # Get exact highlighted text in this block
                    highlight_intersect_text = page.get_text("text", clip=annot.rect).strip()
                    break
        
        highlight_str = f" [HIGHLIGHTED: {highlight_intersect_text}]" if is_highlighted else ""
        print(f"[{round(y0,1)}] {text_clean!r}{highlight_str}")
