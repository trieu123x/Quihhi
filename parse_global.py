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
            # Create a global rect by shifting y coordinates
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
current_chapter = "Chương 1"

idx = 0
while idx < len(global_blocks):
    b = global_blocks[idx]
    text = b["text"]
    
    # Check if it's a chapter header
    if text.lower().startswith("chương "):
        current_chapter = text
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
            
            # If next block starts with a chapter or another question, stop gathering options
            if next_text.lower().startswith("chương ") or re.match(r'^\d+\.\s*', next_text):
                break
            
            # Otherwise, it's an option
            # Check if this option is highlighted
            is_correct = False
            opt_rect = next_b["rect"]
            for annot in global_annots:
                if annot["rect"].intersects(opt_rect):
                    intersect = annot["rect"] & opt_rect
                    # Check if the intersection is significant
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

# Analyze extracted questions
print(f"Total questions extracted: {len(questions)}")
no_correct = 0
one_correct = 0
multi_correct = 0

for q in questions:
    correct_count = sum(1 for opt in q["options"] if opt["is_correct"])
    if correct_count == 0:
        no_correct += 1
    elif correct_count == 1:
        one_correct += 1
    else:
        multi_correct += 1

print(f"Questions with 0 correct answers: {no_correct}")
print(f"Questions with 1 correct answer: {one_correct}")
print(f"Questions with >1 correct answers: {multi_correct}")

# Let's check some questions with 0 correct answers now
if no_correct > 0:
    print("\n--- Sample of questions with 0 correct answers ---")
    count = 0
    for q in questions:
        correct_count = sum(1 for opt in q["options"] if opt["is_correct"])
        if correct_count == 0:
            print(f"Q{q['number']} ({q['chapter']}): {q['question']}")
            for opt in q["options"]:
                print(f"  - {opt['text']} (Correct? {opt['is_correct']})")
            count += 1
            if count >= 10:
                break
                
# Write all extracted questions to questions.json
with open("questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print("\nSaved questions to questions.json")
