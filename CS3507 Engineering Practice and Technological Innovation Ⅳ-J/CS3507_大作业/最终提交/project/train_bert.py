import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import BertTokenizer

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

import torch

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
val_dataset = EmotionDataset(val_encodings, val_labels)

from transformers import BertForSequenceClassification, Trainer, TrainingArguments

model = BertForSequenceClassification.from_pretrained('bert', num_labels=num_labels)

training_args = TrainingArguments(
    output_dir='./model/bert_6f3_4',
    num_train_epochs=5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    save_steps=1000,
    warmup_steps=1000,
    weight_decay=0.01,
    learning_rate=1e-4,
    # logging_dir='./logs',
    # logging_steps=100,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

trainer.train()

trainer.save_model()
# model.save_pretrained('./model/bert_6f3')
# tokenizer.save_pretrained('./model/bert_6f3')

