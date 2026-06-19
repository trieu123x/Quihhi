import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# Fix Q9 Chapter 1
for q in questions:
    if q["number"] == 9 and "Chương 1" in q["chapter"]:
        for opt in q["options"]:
            if opt["text"] == "Vùng mạng LAN-to-WAN":
                opt["is_correct"] = True
                print("Fixed Q9 Chapter 1: Vùng mạng LAN-to-WAN is correct.")

# Fix Q20 Chapter 2
for q in questions:
    if q["number"] == 20 and "Chương 2" in q["chapter"]:
        for opt in q["options"]:
            if opt["text"] == "Dữ liệu / Khả năng":
                opt["is_correct"] = False
                print("Fixed Q20 Chapter 2: Dữ liệu / Khả năng set to False.")

# Fix Q53 Chapter 5
for q in questions:
    if q["number"] == 53 and "Chương 5" in q["chapter"]:
        for opt in q["options"]:
            if opt["text"] == "Tường lửa cá nhân":
                opt["is_correct"] = False
                print("Fixed Q53 Chapter 5: Tường lửa cá nhân set to False.")

# General cleanup and inspection
total_questions = len(questions)
clean_questions = []

for q in questions:
    # Filter out empty options
    q["options"] = [opt for opt in q["options"] if opt["text"].strip()]
    
    if not q["options"]:
        print(f"Warning: Q{q['number']} ({q['chapter']}) has NO options. Skipping.")
        continue
        
    # Ensure options are unique
    seen_opts = set()
    unique_options = []
    for opt in q["options"]:
        opt_text = opt["text"].strip()
        if opt_text not in seen_opts:
            seen_opts.add(opt_text)
            unique_options.append(opt)
    q["options"] = unique_options
    
    # Check correct answers count
    correct_count = sum(1 for opt in q["options"] if opt["is_correct"])
    if correct_count == 0:
        print(f"Warning: Q{q['number']} ({q['chapter']}) has 0 correct answers. Defaulting first option.")
        q["options"][0]["is_correct"] = True
        
    clean_questions.append(q)

print(f"Final clean questions count: {len(clean_questions)}")

# Write to src/questions.json
os.makedirs("src", exist_ok=True)
with open("src/questions.json", "w", encoding="utf-8") as f:
    json.dump(clean_questions, f, ensure_ascii=False, indent=2)

print("Saved clean questions to src/questions.json")
