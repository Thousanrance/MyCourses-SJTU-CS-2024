import torch
import pandas as pd
from tqdm import tqdm
from torch.utils.data import Dataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments

question = "Please read the given text, analyze its sentiment, and select one of the following emotion options: empty, sadness, excitement, neutral, fear, surprise, love, amusement, annoyance, joy, boredom, relief, anger. \nThe text is: "
answer = "\nThe answer is:"

data_path = ["data/Emotions in text_refresh.csv", "data/Emotion Detection from Text_refresh.csv", "data/emotion analysis based on text_refresh.csv"]
# data = pd.read_csv(data_path[1])
data = pd.read_csv("/home/zcy/dsp/ivj/data/gnrt/data10_clear.csv")
texts = data['Text'].tolist()
emotions = data['Emotion'].tolist()


def get_last_word(sentence):
    return sentence.split()[-1]

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model_retrained = GPT2LMHeadModel.from_pretrained("./model/gpt2_trained3")

model_retrained.eval()

test_num = len(data)
right_answer = 0

for i in tqdm(range(0, 0 + test_num)):
    prompt = question + texts[i] + answer

    prompt_encoded = tokenizer.encode(prompt)
    prompt_tensor = torch.tensor([prompt_encoded])

    with torch.no_grad():
        outputs = model_retrained(prompt_tensor)
        predictions = outputs[0]

    predict_id = torch.argmax(predictions[0,-1, :]).item()
    text = tokenizer.decode(prompt_encoded + [predict_id], skip_special_tokens=True)

    print(i + 1, ':', text)
    predict_emotion = get_last_word(text)

    if (predict_emotion == emotions[i]):
        right_answer += 1
    print("The right answer is:", emotions[i])

print("Accuracy:", right_answer * 1.0 / test_num)
