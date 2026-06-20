import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'src\questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Gộp lại: Chương 2.x -> Chương 2:, Luyện tập N.x -> Luyện tập N:
def merge_label(chapter):
    # Chương 2.1: -> Chương 2:
    m = re.match(r'^(Chương 2)\.\d+:$', chapter)
    if m:
        return 'Chương 2:'
    # Luyện tập 1.x: -> Luyện tập 1:
    # Luyện tập 2.x: -> Luyện tập 2:
    m = re.match(r'^(Luyện tập \d+)\.\d+:$', chapter)
    if m:
        return m.group(1) + ':'
    return chapter

for q in data:
    q['chapter'] = merge_label(q.get('chapter', ''))

with open(r'src\questions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! Total: {len(data)} câu")
chapters = {}
for q in data:
    c = q.get('chapter', '')
    chapters[c] = chapters.get(c, 0) + 1
for k, v in sorted(chapters.items()):
    print(f"  {k!r}: {v}")
