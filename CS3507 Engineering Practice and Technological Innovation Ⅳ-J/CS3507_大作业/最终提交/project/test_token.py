import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import BertTokenizer
from transformers import BertForSequenceClassification, Trainer, TrainingArguments
import torch
import numpy as np
from sklearn.metrics import classification_report

class CustomWordPieceTokenizer:
    def __init__(self, custom_vocab, pretrained_model_name_or_path='bert'):
        self.custom_vocab = set(custom_vocab)
        self.bert_tokenizer = BertTokenizer.from_pretrained(pretrained_model_name_or_path)

    def tokenize(self, text):
        words = text.split()
        tokens = []
        for word in words:
            if word in self.custom_vocab:
                tokens.append(word)
            else:
                tokens.extend(self.bert_tokenizer.tokenize(word))
        return tokens

    def encode(self, text, max_length=128, padding='max_length', truncation=True):
        tokens = self.tokenize(text)
        tokens = tokens[:max_length-2]
        tokens = ['[CLS]'] + tokens + ['[SEP]']
        input_ids = self.bert_tokenizer.convert_tokens_to_ids(tokens)
        attention_mask = [1] * len(input_ids)
        
        if padding == 'max_length':
            padding_length = max_length - len(input_ids)
            input_ids = input_ids + ([0] * padding_length)
            attention_mask = attention_mask + ([0] * padding_length)
        
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask
        }

df = pd.read_csv("/home/zcy/dsp/ivj/data/TtForTwo.csv")

texts = df['Text'].tolist()
emotions = df['Emotion'].tolist()

label_encoder = LabelEncoder()
encoded_emotions = label_encoder.fit_transform(emotions)
num_labels = len(label_encoder.classes_)

train_texts, val_texts, train_labels, val_labels = train_test_split(texts, encoded_emotions, test_size=0.1, random_state=42)

custom_vocab = ["anger", "fear", "joy", "love", "sadness", "surprise", "empty", "excitement", "neutral", "amusement", "annoyance", "boredom", "relief"]
tokenizer = CustomWordPieceTokenizer(custom_vocab)

def encode_texts(texts, tokenizer, max_length=128):
    encodings = {'input_ids': [], 'attention_mask': []}
    for text in texts:
        encoding = tokenizer.encode(text, max_length=max_length)
        encodings['input_ids'].append(encoding['input_ids'])
        encodings['attention_mask'].append(encoding['attention_mask'])
    return encodings

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
model = BertForSequenceClassification.from_pretrained("/home/zcy/dsp/ivj/model/bert_6f3_3")
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