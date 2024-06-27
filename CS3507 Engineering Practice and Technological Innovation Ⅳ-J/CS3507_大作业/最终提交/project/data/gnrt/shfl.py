import os
import csv
import random

directory_path = "/home/zcy/dsp/ivj/data/gnrt/"

all_data = []

for filename in os.listdir(directory_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                all_data.append(row)

random.shuffle(all_data)

output_file_path = "/home/zcy/dsp/ivj/data/gnrt/data.csv"
with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['text', 'emotion'])
    writer.writeheader()
    writer.writerows(all_data)

print("finish.")
