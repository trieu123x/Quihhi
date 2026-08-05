import fitz
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = "NganHangCauHoiHDH_DhNguyenTatThanh.pdf"
OUTPUT_PATH = "questions_hdh.json"

doc = fitz.open(PDF_PATH)
print(f"Total pages: {len(doc)}")

# ---- Pass 1: Collect yellow highlight rectangles from drawings ----
# Yellow = fill (1.0, 1.0, 0.0) or close to it
global_highlights = []
page_heights = [doc[i].rect.height for i in range(len(doc))]

current_y_offset = 0
for page_idx in range(len(doc)):
    page = doc[page_idx]
    drawings = page.get_drawings()
    for path in drawings:
        fill = path.get("fill", None)
        if fill is None:
            current_y_offset_tmp = current_y_offset  # needed inside lambda
            continue
        # Check if yellow: R~1, G~1, B~0
        r, g, b = fill[0], fill[1], fill[2] if len(fill) >= 3 else (0, 0, 0)
        if r > 0.85 and g > 0.85 and b < 0.3:  # yellow
            rect = path.get("rect", None)
            if rect:
                global_rect = fitz.Rect(
                    rect.x0,
                    rect.y0 + current_y_offset,
                    rect.x1,
                    rect.y1 + current_y_offset
                )
                global_highlights.append(global_rect)
    current_y_offset += page_heights[page_idx]

print(f"Total yellow highlight rects found: {len(global_highlights)}")
if global_highlights:
    print(f"  Sample rect: {global_highlights[0]}")

# ---- Pass 2: Collect text blocks with global y-offsets ----
global_blocks = []
current_y_offset = 0

for page_idx in range(len(doc)):
    page = doc[page_idx]
    blocks = page.get_text("blocks")
    for b in blocks:
        x0, y0, x1, y1, text, block_no, block_type = b
        text_clean = text.strip()
        if not text_clean:
            continue
        global_rect = fitz.Rect(x0, y0 + current_y_offset, x1, y1 + current_y_offset)
        global_blocks.append({
            "rect": global_rect,
            "text": text_clean,
            "page": page_idx
        })
    current_y_offset += page_heights[page_idx]

# Sort by y then x
global_blocks.sort(key=lambda b: (round(b["rect"].y0, 1), round(b["rect"].x0, 1)))
print(f"Total text blocks: {len(global_blocks)}")

# ---- Helper: check if a block rect is covered by a yellow highlight ----
def is_highlighted(block_rect, highlights, min_area=30):
    for h_rect in highlights:
        # Expand highlight rect slightly to catch boundary issues
        expanded = fitz.Rect(h_rect.x0 - 2, h_rect.y0 - 4, h_rect.x1 + 2, h_rect.y1 + 4)
        if expanded.intersects(block_rect):
            intersect = expanded & block_rect
            if intersect.get_area() > min_area:
                return True
    return False

# ---- Pass 3: Parse chapters, questions and options ----
CHAPTER_PATTERN = re.compile(
    r'^(ch[uư][oơ]ng\s+\d+.*|chapter\s+\d+.*)',
    re.IGNORECASE
)
QUESTION_PATTERN = re.compile(r'^(?:câu\s+)?(\d+)[.:\)]\s*(.*)', re.DOTALL | re.IGNORECASE)
OPTION_PATTERN = re.compile(r'^([A-Da-d])[.:\)]\s*(.*)', re.DOTALL)

questions = []
current_chapter = "Chương 1"

idx = 0
while idx < len(global_blocks):
    b = global_blocks[idx]
    text = b["text"]
    first_line = text.split('\n')[0].strip()

    # Check for chapter header
    if CHAPTER_PATTERN.match(first_line):
        current_chapter = first_line.strip()[:80]
        print(f"  >> Chapter: {current_chapter}")
        idx += 1
        continue

    # Check if it's a question
    q_match = QUESTION_PATTERN.match(first_line)
    if q_match:
        q_num = int(q_match.group(1))
        q_text = q_match.group(2).strip()

        # Append continuation lines that aren't options
        lines_after = text.split('\n')[1:]
        for ln in lines_after:
            ln_stripped = ln.strip()
            if ln_stripped and not OPTION_PATTERN.match(ln_stripped):
                q_text = (q_text + ' ' + ln_stripped).strip()
            else:
                break

        options = []
        idx += 1

        # Gather option blocks
        while idx < len(global_blocks):
            next_b = global_blocks[idx]
            next_text = next_b["text"]
            next_first = next_text.split('\n')[0].strip()

            # Stop at new chapter or question
            if CHAPTER_PATTERN.match(next_first):
                break
            if QUESTION_PATTERN.match(next_first):
                break

            opt_match = OPTION_PATTERN.match(next_first)
            if opt_match:
                opt_letter = opt_match.group(1).upper()
                opt_text = opt_match.group(2).strip()

                # Append continuation
                opt_lines = next_text.split('\n')[1:]
                for oln in opt_lines:
                    oln_stripped = oln.strip()
                    if oln_stripped and not OPTION_PATTERN.match(oln_stripped):
                        opt_text = (opt_text + ' ' + oln_stripped).strip()

                correct = is_highlighted(next_b["rect"], global_highlights)
                options.append({
                    "text": opt_text,
                    "is_correct": correct
                })
                idx += 1
            else:
                idx += 1

        if options:
            questions.append({
                "number": q_num,
                "chapter": current_chapter,
                "question": q_text,
                "options": options
            })
    else:
        idx += 1

print(f"\n=== RESULTS ===")
print(f"Total questions: {len(questions)}")

no_correct = sum(1 for q in questions if sum(o["is_correct"] for o in q["options"]) == 0)
one_correct = sum(1 for q in questions if sum(o["is_correct"] for o in q["options"]) == 1)
multi_correct = sum(1 for q in questions if sum(o["is_correct"] for o in q["options"]) > 1)
print(f"  0 correct: {no_correct}")
print(f"  1 correct: {one_correct}")
print(f"  >1 correct: {multi_correct}")

chapters = {}
for q in questions:
    chapters[q["chapter"]] = chapters.get(q["chapter"], 0) + 1
print("\nPer chapter:")
for ch, cnt in sorted(chapters.items()):
    print(f"  {ch}: {cnt}")

# Show a few to verify
print("\n--- Sample questions with correct answers ---")
shown = 0
for q in questions:
    corrects = [o for o in q["options"] if o["is_correct"]]
    if corrects and shown < 3:
        print(f"Q{q['number']} ({q['chapter']}): {q['question'][:70]}")
        for o in q["options"]:
            mark = "✓" if o["is_correct"] else " "
            print(f"  [{mark}] {o['text'][:60]}")
        shown += 1

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {OUTPUT_PATH}")
