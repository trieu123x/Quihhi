import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'src\questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Gộp phần cuối nhỏ vào phần trước
MERGE_MAP = {
    'Chương 4.3:': 'Chương 4.2:',
    'Chương 5.4:': 'Chương 5.3:',
}

for q in data:
    c = q.get('chapter', '')
    if c in MERGE_MAP:
        q['chapter'] = MERGE_MAP[c]

with open(r'src\questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! Total: {len(data)} câu")
chapters = {}
for q in data:
    c = q.get('chapter', '')
    chapters[c] = chapters.get(c, 0) + 1
for k, v in sorted(chapters.items()):
    print(f"  {k!r}: {v}")
