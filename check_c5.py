import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Current questions.json - Chuong 5
with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

c5 = [q for q in data if q.get('chapter') == 'Chương 5:']
print(f"questions.json - Chương 5: {len(c5)} câu")
if c5:
    print(f"  number range: {c5[0]['number']} -> {c5[-1]['number']}")
    print(f"  Sample: {c5[0]['question'][:60]}...")

# bosungc5.json
with open('bosungc5.json', 'r', encoding='utf-8') as f:
    b5 = json.load(f)

print(f"\nbosungc5.json: {len(b5)} câu")
print(f"  Sample: {b5[0]['text'][:60]}...")

# Check overlap by text similarity (first 40 chars)
existing_texts = set(q['question'][:40] for q in c5)
new_texts = [item for item in b5 if item['text'][:40] not in existing_texts]
print(f"\nCâu mới (chưa có trong Chương 5): {len(new_texts)}")
print(f"Câu trùng lặp: {len(b5) - len(new_texts)}")
