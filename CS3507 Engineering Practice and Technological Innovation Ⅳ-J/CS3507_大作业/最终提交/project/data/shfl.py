import csv
import random

csv_files = [
    "/home/zcy/dsp/ivj/data/Emotion Detection from Text_top.csv",
    "/home/zcy/dsp/ivj/data/emotion analysis based on text_top.csv"
]

all_data = []

for file_path in csv_files:
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            all_data.append(row)

random.shuffle(all_data)

output_file_path = "/home/zcy/dsp/ivj/data/TtForTwo.csv"
with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Text', 'Emotion'])
    writer.writeheader()
    writer.writerows(all_data)

print("finish.")
