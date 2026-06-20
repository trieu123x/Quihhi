import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

def load_flat_smart(path):
    """Parse a file that may contain: one array, multiple arrays, or comma-separated arrays."""
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
    
    # Strategy: wrap the whole thing in [ ] to make it a valid JSON array-of-arrays,
    # then flatten. Handle the case where there may already be a leading [
    # by checking if wrapping produces valid JSON.
    
    # Try direct parse first
    try:
        obj = json.loads(raw)
        if isinstance(obj, list):
            # Flat list or list-of-lists
            if obj and isinstance(obj[0], list):
                return [item for sub in obj for item in sub]
            return obj
    except json.JSONDecodeError:
        pass
    
    # Try wrapping in outer array (handles ]\n[ or ],\n[)
    wrapped = '[' + raw + ']'
    try:
        obj = json.loads(wrapped)
        # obj is now a list of lists
        items = []
        for sub in obj:
            if isinstance(sub, list):
                items.extend(sub)
            else:
                items.append(sub)
        return items
    except json.JSONDecodeError as e:
        print(f"Wrapped parse also failed: {e}")
    
    # Fallback: split on ]\n[ boundaries
    # Replace "]\n[" and "],[" with "," then wrap
    fixed = re.sub(r'\]\s*,?\s*\[', ',', raw)
    fixed = '[' + fixed + ']'
    try:
        obj = json.loads(fixed)
        return obj
    except json.JSONDecodeError as e:
        print(f"Regex-split parse failed: {e}")
        return []

# ---- Test ----
b5_raw = load_flat_smart('bosungc5.json')
print(f"bosungc5.json parsed: {len(b5_raw)} items")

# De-dup by id
seen_ids = set()
b5 = []
for item in b5_raw:
    iid = item.get('id')
    if iid not in seen_ids:
        seen_ids.add(iid)
        b5.append(item)
print(f"After dedup by id: {len(b5)}")

# ---- Load questions.json ----
with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

c5_existing = [q for q in data if q.get('chapter') == 'Chương 5:']
print(f"\nChương 5 hiện tại: {len(c5_existing)} câu")

# De-dup by text
existing_texts = set(q['question'][:50].strip() for q in c5_existing)
new_items = [item for item in b5 if item['text'][:50].strip() not in existing_texts]

print(f"Câu mới chưa có trong Chương 5: {len(new_items)}")
print(f"Câu bị bỏ qua (trùng): {len(b5) - len(new_items)}")

if not new_items:
    print("Không có câu mới để thêm!")
    sys.exit(0)

# ---- Append ----
max_num = max(q.get('number', 0) for q in data)
print(f"Max number hiện tại: {max_num}")

new_entries = []
for i, item in enumerate(new_items):
    new_entries.append({
        "number": max_num + i + 1,
        "chapter": "Chương 5:",
        "question": item['text'],
        "options": [
            {"text": ans['text'], "is_correct": ans['isCorrect']}
            for ans in item.get('answers', [])
        ]
    })

merged = data + new_entries

with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"\nĐã thêm {len(new_entries)} câu mới vào Chương 5")
print(f"  Số thứ tự: {new_entries[0]['number']} -> {new_entries[-1]['number']}")
print(f"\nTổng cộng: {len(merged)} câu")

# Summary
chapters = {}
for q in merged:
    c = q.get('chapter', '')
    chapters[c] = chapters.get(c, 0) + 1
for k, v in sorted(chapters.items()):
    print(f"  {k!r}: {v}")
