import json

# Load existing questions
with open('questions.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)

# Load supplement file
with open('bosungc3.json', 'r', encoding='utf-8') as f:
    new_raw = json.load(f)

# De-duplicate against ALL existing questions
all_texts = set(q['question'].strip() for q in existing)

# Find the highest number used in chapter 3
ch3_nums = [q['number'] for q in existing if q['chapter'].startswith('Chương 3')]
next_num = max(ch3_nums) + 1 if ch3_nums else 1

# Find insertion point: right after the last Chương 3 question in the list
last_ch3_idx = max(
    (i for i, q in enumerate(existing) if q['chapter'].startswith('Chương 3')),
    default=len(existing) - 1
)

# Convert new questions to target format
converted = []
skipped = 0
for item in new_raw:
    question_text = item['text'].strip()
    
    # Skip if this exact question already exists anywhere in the file
    if question_text in all_texts:
        skipped += 1
        continue
    
    options = [
        {
            'text': a['text'].strip(),
            'is_correct': a['isCorrect']
        }
        for a in item['answers']
    ]
    
    new_q = {
        'number': next_num,
        'chapter': 'Chương 3:',
        'question': question_text,
        'options': options
    }
    converted.append(new_q)
    all_texts.add(question_text)  # prevent duplicates within bosungc3 itself
    next_num += 1

print(f"Tổng câu hỏi mới: {len(converted)}")
print(f"Câu bị bỏ qua (trùng): {skipped}")

# Insert after last chapter 3 entry
merged = existing[:last_ch3_idx + 1] + converted + existing[last_ch3_idx + 1:]

# Save result
with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"Đã lưu questions.json. Tổng: {len(merged)} câu.")
print(f"Chương 3 hiện có: {sum(1 for q in merged if q['chapter'].startswith('Chương 3'))} câu.")
