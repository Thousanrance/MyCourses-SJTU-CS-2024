import csv

input_file_path = "/home/zcy/dsp/ivj/data/gnrt/data10.csv"
output_file_path = "/home/zcy/dsp/ivj/data/gnrt/data10_clear.csv"

unique_data = []
seen_texts = set()

with open(input_file_path, 'r', encoding='utf-8') as input_file:
    reader = csv.DictReader(input_file)
    for row in reader:
        if row['Text'] not in seen_texts:
            unique_data.append(row)
            seen_texts.add(row['Text'])

with open(output_file_path, 'w', newline='', encoding='utf-8') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=['Text', 'Emotion'])
    writer.writeheader()
    writer.writerows(unique_data)

print("finish.")
