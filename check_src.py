import json, sys, math
sys.stdout.reconfigure(encoding='utf-8')

with open(r'src\questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total: {len(data)} questions")
chapters = {}
for q in data:
    c = q.get('chapter', '')
    chapters[c] = chapters.get(c, 0) + 1
for k, v in sorted(chapters.items()):
    parts = math.ceil(v / 60)
    print(f"  {k!r}: {v} questions -> cần tách thành {parts} phần" if v > 60 else f"  {k!r}: {v} questions -> OK")
