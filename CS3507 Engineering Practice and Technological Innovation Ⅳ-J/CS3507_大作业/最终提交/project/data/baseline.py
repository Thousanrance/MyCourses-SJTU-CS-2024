import torch
import pandas as pd
from tqdm import tqdm
from torch.utils.data import Dataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments


df = pd.read_csv("emotion analysis based on text_refresh.csv")

grouped = df.groupby('Emotion')

top_10_per_emotion = pd.DataFrame(columns=df.columns)

for emotion, group in grouped:
    if len(group) >= 800:
        top_10 = group.head(800)
    else:
        top_10 = group
    top_10_per_emotion = pd.concat([top_10_per_emotion, top_10])

top_10_per_emotion.to_csv("emotion analysis based on text_top.csv", index=False)

print("Results saved")