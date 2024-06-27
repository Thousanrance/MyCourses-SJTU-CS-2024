import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import BertTokenizer
from transformers import BertForSequenceClassification, Trainer, TrainingArguments
import torch
import numpy as np
from sklearn.metrics import classification_report

df = pd.read_csv("/home/zcy/dsp/ivj/data/SixForThree_800.csv")

texts = df['Text'].tolist()
emotions = df['Emotion'].tolist()

label_encoder = LabelEncoder()
encoded_emotions = label_encoder.fit_transform(emotions)
num_labels = len(label_encoder.classes_)

train_texts, val_texts, train_labels, val_labels = train_test_split(texts, encoded_emotions, test_size=0.1, random_state=42)

tokenizer = BertTokenizer.from_pretrained('bert')

def encode_texts(texts, tokenizer, max_length=128):
    return tokenizer(texts, padding=True, truncation=True, max_length=max_length, return_tensors='pt')

train_encodings = encode_texts(train_texts, tokenizer)
val_encodings = encode_texts(val_texts, tokenizer)

class EmotionDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = EmotionDataset(train_encodings, train_labels)
test_dataset = EmotionDataset(val_encodings, val_labels)

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model = BertForSequenceClassification.from_pretrained("/home/zcy/dsp/ivj/model/bert_6f3_2")
model.to(device)

model.eval()

test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=16, shuffle=False)

all_preds = []
all_labels = []

with torch.no_grad():
    for batch in test_loader:
        inputs = {key: val.to(device) for key, val in batch.items() if key != 'labels'}
        labels = batch['labels'].to(device)
        outputs = model(**inputs)
        preds = torch.argmax(outputs.logits, axis=-1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

report = classification_report(all_labels, all_preds, target_names=label_encoder.classes_, digits=8)
print(report)