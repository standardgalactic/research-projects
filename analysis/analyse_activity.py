import csv
from collections import Counter, defaultdict
from datetime import datetime
import math

try:
    import matplotlib.pyplot as plt
    plotting = True
except ImportError:
    plotting = False

filename = "following-activity.csv"

active_lang = Counter()
inactive_lang = Counter()

age_bins = defaultdict(lambda: {"active":0,"inactive":0})

total_active = 0
total_inactive = 0

now = datetime.utcnow()

def year_bin(age):
    return int(age // 1)

with open(filename, newline="", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    for row in reader:

        status = row["status"]
        lang = row["primary_language"]
        created = row["created_at"]

        if not lang or lang.lower() == "null":
            lang = "None"

        if status == "ACTIVE":
            active_lang[lang] += 1
            total_active += 1
        else:
            inactive_lang[lang] += 1
            total_inactive += 1

        if created and created != "null":
            created_time = datetime.fromisoformat(created.replace("Z",""))
            age_years = (now - created_time).days / 365.25
            b = year_bin(age_years)

            if status == "ACTIVE":
                age_bins[b]["active"] += 1
            else:
                age_bins[b]["inactive"] += 1


print("\nTOTAL ACTIVE:", total_active)
print("TOTAL INACTIVE:", total_inactive)

print("\nLanguage Activity Ratios (top 25 by total presence)\n")

all_lang = set(active_lang) | set(inactive_lang)

stats = []

for lang in all_lang:

    a = active_lang[lang]
    i = inactive_lang[lang]
    total = a + i

    if total < 100:
        continue

    ratio = a / total
    stats.append((lang,a,i,ratio,total))

stats.sort(key=lambda x: x[4], reverse=True)

for lang,a,i,ratio,total in stats[:25]:

    print(f"{lang:20} active={a:8} inactive={i:8}  activity_ratio={ratio:6.3f}")


print("\nAccount Age Survival\n")

ages = sorted(age_bins.keys())

survival = []

for a in ages:

    active = age_bins[a]["active"]
    inactive = age_bins[a]["inactive"]
    total = active + inactive

    if total == 0:
        continue

    p = active / total
    survival.append((a,p))

    print(f"age {a:2} years  active_fraction={p:6.3f}")

if survival:

    half_life = None

    for age,p in survival:
        if p < 0.5:
            half_life = age
            break

    if half_life is not None:
        print("\nApproximate developer activity half-life:", half_life,"years")

if plotting:

    xs = [x for x,_ in survival]
    ys = [y for _,y in survival]

    plt.figure()
    plt.plot(xs,ys)
    plt.xlabel("Account age (years)")
    plt.ylabel("Active fraction")
    plt.title("Developer Activity Survival Curve")
    plt.grid(True)
    plt.show()
