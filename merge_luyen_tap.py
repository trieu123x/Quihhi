import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# ---- Load questions.json ----
with open('questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

max_num = max(q.get('number', 0) for q in data)
print(f"Current questions.json: {len(data)} questions, max number = {max_num}")

# ---- Helper: flatten a possibly nested list-of-arrays JSON ----
def load_flat(path):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read().strip()

    # The files may contain multiple JSON arrays concatenated – parse them all
    items = []
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(raw):
        # skip whitespace
        while pos < len(raw) and raw[pos] in ' \t\r\n':
            pos += 1
        if pos >= len(raw):
            break
        obj, end = decoder.raw_decode(raw, pos)
        if isinstance(obj, list):
            items.extend(obj)
        else:
            items.append(obj)
        pos = end
    return items

# ---- Load luyentap files ----
lt1 = load_flat('luyentap1.json')
lt2 = load_flat('luyentap2.json')

print(f"luyentap1.json raw entries: {len(lt1)}")
print(f"luyentap2.json raw entries: {len(lt2)}")

# ---- De-duplicate by question id within each file ----
def dedup(items):
    seen = set()
    out = []
    for item in items:
        if item['id'] not in seen:
            seen.add(item['id'])
            out.append(item)
    return out

lt1 = dedup(lt1)
lt2 = dedup(lt2)
print(f"luyentap1 after dedup: {len(lt1)}")
print(f"luyentap2 after dedup: {len(lt2)}")

# ---- Convert and append ----
def convert(items, chapter):
    entries = []
    for item in items:
        if not item.get('answers'):
            continue
        entries.append({
            "question": item['text'],
            "chapter": chapter,
            "options": [
                {"text": ans['text'], "is_correct": ans['isCorrect']}
                for ans in item['answers']
            ]
        })
    return entries

lt1_entries = convert(lt1, "Luyện tập 1:")
lt2_entries = convert(lt2, "Luyện tập 2:")

print(f"\nConverted luyentap1: {len(lt1_entries)} questions")
print(f"Converted luyentap2: {len(lt2_entries)} questions")

# Assign sequential numbers
counter = max_num + 1
for e in lt1_entries + lt2_entries:
    e['number'] = counter
    counter += 1

merged = data + lt1_entries + lt2_entries

# ---- Save ----
with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"\nDone! Total questions: {len(merged)}")

# ---- Chapter summary ----
chapters = {}
for q in merged:
    c = q.get('chapter', '')
    chapters[c] = chapters.get(c, 0) + 1
for k, v in sorted(chapters.items()):
    print(f"  {k!r}: {v}")
