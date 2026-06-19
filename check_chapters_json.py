import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
with open("src/questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

chapter_counts = {}
for q in questions:
    ch = q["chapter"]
    chapter_counts[ch] = chapter_counts.get(ch, 0) + 1

for ch, count in chapter_counts.items():
    print(f"Chapter: {ch!r} | Count: {count}")
