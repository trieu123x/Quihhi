import json, sys
sys.stdout.reconfigure(encoding='utf-8')

def load_flat_debug(path):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
    items = []
    decoder = json.JSONDecoder()
    pos = 0
    array_count = 0
    while pos < len(raw):
        # skip whitespace
        while pos < len(raw) and raw[pos] in ' \t\r\n':
            pos += 1
        if pos >= len(raw):
            break
        try:
            obj, end = decoder.raw_decode(raw, pos)
        except json.JSONDecodeError as e:
            print(f"\n!!! Parse error at pos {pos} (char {e.pos}): {e.msg}")
            print(f"Context: {repr(raw[max(0,e.pos-50):e.pos+50])}")
            break
        array_count += 1
        if isinstance(obj, list):
            print(f"Array #{array_count}: {len(obj)} items (pos {pos}-{end})")
            items.extend(obj)
        else:
            items.append(obj)
        pos = end
    return items

items = load_flat_debug('bosungc5.json')
print(f"\nTotal parsed: {len(items)}")
