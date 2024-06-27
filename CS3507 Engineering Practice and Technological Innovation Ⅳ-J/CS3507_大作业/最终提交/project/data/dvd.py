import csv
import random
from collections import defaultdict

input_file_path = "/home/zcy/dsp/ivj/data/SixForThree_800.csv"
train_file_path = "/home/zcy/dsp/ivj/data/SixForThree_800_train.csv"
val_file_path = "/home/zcy/dsp/ivj/data/SixForThree_800_val.csv"

data_by_emotion = defaultdict(list)

with open(input_file_path, 'r', encoding='utf-8') as input_file:
    reader = csv.DictReader(input_file)
    for row in reader:
        data_by_emotion[row['Emotion']].append(row)

train_data = []
val_data = []

for emotion, data in data_by_emotion.items():
    split_idx = int(0.8 * len(data))
    train_data.extend(data[:split_idx])
    val_data.extend(data[split_idx:])

random.shuffle(train_data)
random.shuffle(val_data)

with open(train_file_path, 'w', newline='', encoding='utf-8') as train_file:
    writer = csv.DictWriter(train_file, fieldnames=['Text', 'Emotion'])
    writer.writeheader()
    writer.writerows(train_data)

with open(val_file_path, 'w', newline='', encoding='utf-8') as val_file:
    writer = csv.DictWriter(val_file, fieldnames=['Text', 'Emotion'])
    writer.writeheader()
    writer.writerows(val_data)

print("finish.")
