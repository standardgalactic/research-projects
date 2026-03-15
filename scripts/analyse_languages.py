import csv
from collections import Counter

filename = "following-activity.csv"

active_lang = Counter()
inactive_lang = Counter()

total_active = 0
total_inactive = 0

with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        status = row["status"]
        lang = row["primary_language"]

        if not lang or lang.lower() == "null":
            lang = "None"

        if status == "ACTIVE":
            active_lang[lang] += 1
            total_active += 1
        elif status == "INACTIVE":
            inactive_lang[lang] += 1
            total_inactive += 1

print("\nACTIVE ACCOUNTS:", total_active)
print("INACTIVE ACCOUNTS:", total_inactive)

print("\nTop languages among ACTIVE accounts:\n")

for lang, count in active_lang.most_common(20):
    pct = (count / total_active) * 100
    print(f"{lang:20} {count:10}  {pct:6.2f}%")

print("\nTop languages among INACTIVE accounts:\n")

for lang, count in inactive_lang.most_common(20):
    pct = (count / total_inactive) * 100
    print(f"{lang:20} {count:10}  {pct:6.2f}%")
