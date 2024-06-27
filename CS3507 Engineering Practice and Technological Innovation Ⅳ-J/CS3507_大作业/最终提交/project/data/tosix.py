import csv

input_file_path = "/home/zcy/dsp/ivj/data/emotion analysis based on text_top.csv"
output_file_path = "/home/zcy/dsp/ivj/data/emotion analysis based on text_filter.csv"

with open(input_file_path, 'r', encoding='utf-8') as input_file:
    reader = csv.DictReader(input_file)
    filtered_data = [row for row in reader if row['Emotion'] in {'anger', 'fear', 'joy', 'love', 'sadness', 'surprise'}]

with open(output_file_path, 'w', newline='', encoding='utf-8') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=['Text', 'Emotion'])
    writer.writeheader()
    writer.writerows(filtered_data)

print("finish.")
