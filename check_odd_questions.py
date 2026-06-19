import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

print("--- Questions with >1 correct answer ---")
for q in questions:
    corrects = [opt for opt in q["options"] if opt["is_correct"]]
    if len(corrects) > 1:
        print(f"Q{q['number']} ({q['chapter']}): {q['question']}")
        for opt in q["options"]:
            print(f"  - {opt['text']} (Correct? {opt['is_correct']})")

print("\n--- Question 9 in detail ---")
for q in questions:
    if q["number"] == 9 and "Chương 1" in q["chapter"]:
        print(f"Q{q['number']} ({q['chapter']}): {q['question']}")
        for opt in q["options"]:
            print(f"  - {opt['text']} (Correct? {opt['is_correct']})")
