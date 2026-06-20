import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

chapters = {}
for q in data:
    c = q.get('chapter', '')
    chapters[c] = chapters.get(c, 0) + 1

for k, v in sorted(chapters.items()):
    print(f"  {k!r}: {v} questions")

print(f"\nTotal: {len(data)} questions")
max_num = max(q.get('number', 0) for q in data)
print(f"Max number: {max_num}")
