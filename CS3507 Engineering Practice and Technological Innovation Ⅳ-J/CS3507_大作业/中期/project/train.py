import torch
import pandas as pd
from tqdm import tqdm
from torch.utils.data import Dataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments



question = "Please read the given text, analyze its sentiment, and select one of the following emotion options: empty, sadness, excitement, neutral, fear, surprise, love, amusement, annoyance, joy, boredom, relief, anger. \nThe text is: "
answer = "\nThe answer is:"

data_path = ["data/Emotions in text_top.csv", "data/Emotion Detection from Text_top.csv", "data/emotion analysis based on text_top.csv"]
data = pd.read_csv(data_path[0])
texts = data['Text'].tolist()
emotions = data['Emotion'].tolist()

train_num = len(data)

usable_data = []
for i in range(train_num):
    full_text = question + texts[i] + answer + ' ' + emotions[i]
    usable_data.append(full_text)

# print(usable_data)

def get_last_word(sentence):
    return sentence.split()[-1]
    

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("model/gpt2_trained2")




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


training_args = TrainingArguments(
    output_dir='./model/gpt2_trained3',
    num_train_epochs=3,
    per_device_train_batch_size=1,
    save_steps=1000,
    learning_rate=1e-4,
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

