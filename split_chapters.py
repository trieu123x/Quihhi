import json, sys, math
sys.stdout.reconfigure(encoding='utf-8')

# Chương nào cần tách (> 60 câu)
CHAPTERS_TO_SPLIT = {
    'Chương 2:', 'Chương 3:', 'Chương 4:', 'Chương 5:',
    'Luyện tập 1:', 'Luyện tập 2:'
}
CHUNK_SIZE = 60

with open(r'src\questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Nhóm theo chapter, giữ thứ tự
chapter_groups = {}
chapter_order = []
for q in data:
    c = q.get('chapter', '')
    if c not in chapter_groups:
        chapter_groups[c] = []
        chapter_order.append(c)
    chapter_groups[c].append(q)

result = []
for chapter in chapter_order:
    questions = chapter_groups[chapter]
    base = chapter.rstrip(':').strip()  # e.g., "Chương 3"
    
    if chapter in CHAPTERS_TO_SPLIT and len(questions) > CHUNK_SIZE:
        n_parts = math.ceil(len(questions) / CHUNK_SIZE)
        for part in range(n_parts):
            part_label = f"{base}.{part+1}:"
            chunk = questions[part * CHUNK_SIZE : (part + 1) * CHUNK_SIZE]
            for q in chunk:
                new_q = dict(q)
                new_q['chapter'] = part_label
                result.append(new_q)
        print(f"{chapter!r}: {len(questions)} câu -> tách thành {n_parts} phần ({base}.1 .. {base}.{n_parts}:)")
    else:
        for q in questions:
            result.append(q)
        print(f"{chapter!r}: {len(questions)} câu -> giữ nguyên")

# Lưu
with open(r'src\questions.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\nDone! Total: {len(result)} câu")

# Summary
chapters = {}
for q in result:
    c = q.get('chapter', '')
    chapters[c] = chapters.get(c, 0) + 1
for k, v in sorted(chapters.items()):
    print(f"  {k!r}: {v}")
