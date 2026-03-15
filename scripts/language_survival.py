import csv
from collections import Counter, defaultdict
from datetime import datetime
import statistics

filename = "following-activity.csv"

active_lang = Counter()
inactive_lang = Counter()
lifetimes = defaultdict(list)

def clean_lang(x):
    if not x:
        return "None"
    x = x.strip()
    if x.lower() == "null":
        return "None"
    return x

def parse_time(t):
    if not t or t == "null":
        return None
    try:
        return datetime.fromisoformat(t.replace("Z",""))
    except:
        return None

with open(filename, newline="", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    for row in reader:

        lang = clean_lang(row.get("primary_language"))
        status = row.get("status")

        created = parse_time(row.get("created_at"))
        pushed = parse_time(row.get("last_pushed_at"))

        if status == "ACTIVE":
            active_lang[lang] += 1
        elif status == "INACTIVE":
            inactive_lang[lang] += 1

        if created and pushed:
            age = (pushed - created).days / 365.25
            lifetimes[lang].append(age)

print("\nLanguage activity ratios\n")

langs = set(active_lang) | set(inactive_lang)

stats = []

for lang in langs:

    a = active_lang[lang]
    i = inactive_lang[lang]
    total = a + i

    if total < 20:
        continue

    ratio = a / total
    stats.append((lang,a,i,total,ratio))

stats.sort(key=lambda x: x[3], reverse=True)

for lang,a,i,total,ratio in stats[:30]:
    print(f"{lang:18} active={a:7} inactive={i:7} total={total:7} ratio={ratio:5.2f}")

print("\nMedian developer lifetimes by language\n")

life_stats = []

for lang,vals in lifetimes.items():

    if len(vals) < 20:
        continue

    median = statistics.median(vals)
    life_stats.append((lang,median,len(vals)))

life_stats.sort(key=lambda x: x[1], reverse=True)

for lang,median,count in life_stats[:20]:
    print(f"{lang:18} median_lifetime={median:5.2f} years  n={count}")