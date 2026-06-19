import fitz
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open("cau-hoi-on-tap-csattt-ptit.pdf")

# Page 33 is Chapter 4
print("--- Page 33 blocks ---")
for b in doc[33].get_text("blocks"):
    print(f"Block: {b[4].strip()!r}")

# Page 47 is Chapter 5
print("\n--- Page 47 blocks ---")
for b in doc[47].get_text("blocks"):
    print(f"Block: {b[4].strip()!r}")
