import torch
import pandas as pd
from torch.utils.data import Dataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments

class LoveLettersDataset(Dataset):
    def __init__(self, data_file, tokenizer, max_length=512):
        self.data = []
        with open(data_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 2000:
                    break
                self.data.append(tokenizer.encode(line.strip(), max_length=max_length, truncation=True))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return torch.tensor(self.data[idx])

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('./model/gnrt_surprise_2')

# data_file = "/home/zcy/dsp/ivj/data/Emotions in text_refresh.csv"

# dataset = LoveLettersDataset(data_file, tokenizer)

data_path = ["data/Emotions in text_refresh.csv", "data/Emotion Detection from Text_refresh.csv", "data/emotion analysis based on text_top.csv"]
data = pd.read_csv(data_path[2])
texts = data['Text'].tolist()
emotions = data['Emotion'].tolist()

train_num = len(data)

usable_data = []
cnt = 0
for i in range(train_num):
    if emotions[i] != 'surprise':
        continue
    cnt += 1
    if cnt > 4000:
        continue
    full_text = texts[i]
    usable_data.append(full_text)

class EmotionalTextDataset(Dataset):
    def __init__(self, usable_data, tokenizer):
        self.data = []
        for text in usable_data:
            self.data.append(tokenizer.encode(text, max_length=1024, truncation=True))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return torch.tensor(self.data[idx])

dataset = EmotionalTextDataset(usable_data, tokenizer)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

batch_size = 1
num_epochs = 5
learning_rate = 1e-4

training_args = TrainingArguments(
    output_dir='./model/gnrt_surprise_3',
    num_train_epochs=num_epochs,
    per_device_train_batch_size=batch_size,
    save_steps=5000,
    learning_rate=learning_rate,
    overwrite_output_dir=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=dataset,
)

trainer.train()

trainer.save_model()

