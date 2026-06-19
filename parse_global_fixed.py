import fitz
import sys
import re
import json

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
    if not t:
        return True
    if "lomoarcpsd" in t:
        return True
    for w in WATERMARKS:
        if w in t:
            return True
    return False

def clean_text(text):
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if is_watermark(line):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")

# Accumulate all blocks and annotations into a single global space
global_blocks = []
global_annots = []

current_y_offset = 0

for page_idx in range(1, len(doc)):
    page = doc[page_idx]
    page_rect = page.rect
    page_height = page_rect.height
    
    # Extract annotations
    annots = list(page.annots())
    for annot in annots:
        h = annot.rect.y1 - annot.rect.y0
        if h < 45: # Filter out giant annotations
            global_rect = fitz.Rect(
                annot.rect.x0,
                annot.rect.y0 + current_y_offset,
                annot.rect.x1,
                annot.rect.y1 + current_y_offset
            )
            global_annots.append({
                "rect": global_rect,
                "text": page.get_text("text", clip=annot.rect).strip()
            })
            
    # Extract text blocks
    blocks = page.get_text("blocks")
    for b in blocks:
        x0, y0, x1, y1, text, block_no, block_type = b
        text_clean = clean_text(text)
        if not text_clean:
            continue
        
        global_rect = fitz.Rect(
            x0,
            y0 + current_y_offset,
            x1,
            y1 + current_y_offset
        )
        
        global_blocks.append({
            "rect": global_rect,
            "text": text_clean,
            "page": page_idx
        })
        
    current_y_offset += page_height

# Sort global blocks by y coordinate, then x coordinate
global_blocks = sorted(global_blocks, key=lambda b: (round(b["rect"].y0, 1), round(b["rect"].x0, 1)))

# Let's parse the sorted global blocks
questions = []
current_chapter = "Chương 1:"

idx = 0
while idx < len(global_blocks):
    b = global_blocks[idx]
    text = b["text"]
    
    # Clean text to detect chapter
    clean_ch = re.sub(r'^[\s/\\\-\*]+', '', text.strip())
    if clean_ch.lower().startswith("chương "):
        # Extract the chapter title cleanly
        # e.g., "Chương 4 :" -> "Chương 4"
        ch_match = re.match(r'^(chương\s+\d+)', clean_ch, re.IGNORECASE)
        if ch_match:
            current_chapter = ch_match.group(1).title() + ":"
        else:
            current_chapter = clean_ch
        idx += 1
        continue
        
    # Check if it starts with a question number like "1. ", "12. "
    match = re.match(r'^(\d+)\.\s*(.*)', text, re.DOTALL)
    if match:
        q_num = int(match.group(1))
        q_text = match.group(2).strip()
        
        options = []
        idx += 1
        
        # Gather options until next question or next chapter
        while idx < len(global_blocks):
            next_b = global_blocks[idx]
            next_text = next_b["text"]
            
            next_clean = re.sub(r'^[\s/\\\-\*]+', '', next_text.strip())
            
            # If next block starts with a chapter or another question, stop gathering options
            if next_clean.lower().startswith("chương ") or re.match(r'^\d+\.\s*', next_text):
                break
            
            # Otherwise, it's an option
            is_correct = False
            opt_rect = next_b["rect"]
            for annot in global_annots:
                if annot["rect"].intersects(opt_rect):
                    intersect = annot["rect"] & opt_rect
                    if intersect.get_area() > 15:
                        is_correct = True
                        break
                        
            options.append({
                "text": next_text,
                "is_correct": is_correct
            })
            idx += 1
            
        questions.append({
            "number": q_num,
            "chapter": current_chapter,
            "question": q_text,
            "options": options
        })
    else:
        idx += 1

# Let's count chapter distributions
chapter_counts = {}
for q in questions:
    ch = q["chapter"]
    chapter_counts[ch] = chapter_counts.get(ch, 0) + 1

for ch, count in chapter_counts.items():
    print(f"Chapter: {ch!r} | Count: {count}")
    
# Write raw questions
with open("questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print("Saved questions.json")
