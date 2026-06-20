import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# ---- 1. Load questions.json ----
with open(r'C:\Users\admin\Downloads\on-atbm\questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ---- 2. Fix all chapter names: "Chuong N:" -> "Chương N:" ----
fixed = 0
for q in data:
    c = q.get('chapter', '')
    new_c = re.sub(r'Chuong\s+(\d+):', lambda m: f'Chương {m.group(1)}:', c)
    if new_c != c:
        q['chapter'] = new_c
        fixed += 1

print(f"Fixed {fixed} chapter names (Chuong -> Chương)")

# ---- 3. Chapter distribution ----
chapters = {}
for q in data:
    c = q.get('chapter', '')
    chapters[c] = chapters.get(c, 0) + 1
for k, v in sorted(chapters.items()):
    print(f"  {k!r}: {v} questions")

# ---- 4. Load bosungc4.json and append ----
with open(r'C:\Users\admin\Downloads\on-atbm\bosungc4.json', 'r', encoding='utf-8') as f:
    bosungc4 = json.load(f)

max_num = max(q.get('number', 0) for q in data)
print(f"Max number before append: {max_num}")

new_entries = []
for i, item in enumerate(bosungc4):
    new_entries.append({
        "number": max_num + i + 1,
        "chapter": "Chương 4:",
        "question": item["text"],
        "options": [
            {"text": ans["text"], "is_correct": ans["isCorrect"]}
            for ans in item["answers"]
        ]
    })

print(f"Appending {len(new_entries)} questions (number {max_num+1} to {max_num+len(new_entries)})")

merged = data + new_entries

# ---- 5. Save ----
with open(r'C:\Users\admin\Downloads\on-atbm\questions.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"Done! Total: {len(merged)} questions.")
