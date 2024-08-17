import csv
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt

path_data = Path("data", "marker_mpterm.csv")

with open(path_data, "r") as f:
    reader = csv.reader(f)
    header = next(reader)
    marker_mpterm = defaultdict(set)
    for row in reader:
        marker, mpterm = row
        marker_mpterm[marker].add(mpterm)


d = {"A": 1, "B": 2, "C": 3}

with open("data/overlap_ratios_py.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["marker1", "marker2", "intersect_count", "union_count", "overlap_ratio"])
    for a, b in combinations(marker_mpterm, 2):
        intersect_count = len(marker_mpterm[a] & marker_mpterm[b])
        union_count = len(marker_mpterm[a] | marker_mpterm[b])
        overlap = intersect_count / union_count
        if overlap > 0:
            writer.writerow([a, b, intersect_count, union_count, round(overlap, 3)])


path_results = Path("data", "overlap_ratios_py.csv")
with open(path_results, "r") as f:
    reader = csv.reader(f)
    header = next(reader)
    count_intersect = defaultdict(int)
    for row in reader:
        marker1, marker2, intersect_count, union_count, overlap_ratio = row
        count_intersect[intersect_count] += 1

print(count_intersect)


# Sort the data by keys to ensure the plot is ordered numerically
sorted_data = dict(sorted(count_intersect.items(), key=lambda item: int(item[0])))

# Create a bar plot
plt.figure(figsize=(10, 6))
plt.bar(sorted_data.keys(), sorted_data.values(), color="skyblue")
plt.xlabel("Category")
plt.ylabel("Frequency")
plt.title("Bar Plot of Frequency Data")
plt.xticks(rotation=45)
plt.grid(axis="y")

# Show the plot
plt.show()
