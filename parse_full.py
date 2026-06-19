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
    # Remove Studocu watermarks inside text if any
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if is_watermark(line):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")

questions = []
current_chapter = "Chương 1"

for page_idx in range(1, len(doc)):
    page = doc[page_idx]
    annots = list(page.annots())
    
    # Filter out giant annotations (height > 40)
    valid_annots = []
    for annot in annots:
        h = annot.rect.y1 - annot.rect.y0
        if h < 45:  # Valid highlight for an option
            valid_annots.append(annot)
            
    blocks = page.get_text("blocks")
    # Sort blocks by y coordinate, then x coordinate
    blocks = sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))
    
    # Let's group lines/blocks into questions and options
    temp_blocks = []
    for b in blocks:
        x0, y0, x1, y1, text, block_no, block_type = b
        text_clean = clean_text(text)
        if not text_clean:
            continue
        temp_blocks.append({
            "rect": fitz.Rect(x0, y0, x1, y1),
            "text": text_clean
        })
        
    # Now parse the temp_blocks
    idx = 0
    while idx < len(temp_blocks):
        b = temp_blocks[idx]
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
            
            # The next blocks should be choices (usually 4)
            options = []
            idx += 1
            
            # Gather options until next question or next chapter or page ends
            while idx < len(temp_blocks):
                next_b = temp_blocks[idx]
                next_text = next_b["text"]
                
                # If next block starts with a chapter or another question, stop gathering options
                if next_text.lower().startswith("chương ") or re.match(r'^\d+\.\s*', next_text):
                    break
                
                # Otherwise, it's an option
                # Check if this option is highlighted
                is_correct = False
                opt_rect = next_b["rect"]
                for annot in valid_annots:
                    # Check intersection area relative to option height
                    if annot.rect.intersects(opt_rect):
                        intersect = annot.rect & opt_rect
                        if intersect.get_area() > 15: # threshold
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
            # Junk block or text that doesn't match question pattern (like intermediate header or text page)
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

# Let's inspect some of the questions with 0 correct answers
if no_correct > 0:
    print("\n--- Sample of questions with 0 correct answers ---")
    count = 0
    for q in questions:
        correct_count = sum(1 for opt in q["options"] if opt["is_correct"])
        if correct_count == 0:
            print(f"Q{q['number']} ({q['chapter']}): {q['question']}")
            for opt in q["options"]:
                print(f"  - {opt['text']}")
            count += 1
            if count >= 5:
                break
