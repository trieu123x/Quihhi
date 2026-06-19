import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
with open("src/questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

for q in questions:
    if "Bộ lọc địa chỉ MAC" in q["question"]:
        print(f"Question {q['number']} ({q['chapter']}):")
        for opt in q["options"]:
            print(f"  - {opt['text']} (Correct? {opt['is_correct']})")
