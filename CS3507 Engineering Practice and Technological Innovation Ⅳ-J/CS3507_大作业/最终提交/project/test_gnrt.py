from transformers import GPT2Tokenizer, GPT2LMHeadModel
from tqdm import tqdm
import csv

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("model/gnrt_fear_3")

model.eval()

prompt = ["I"]

gen_text = []

for i in tqdm(range(500)):
    prompt_encoded = tokenizer.encode(prompt[0], return_tensors='pt')
    output = model.generate(
        prompt_encoded, 
        do_sample=True,
        max_length=10,
        pad_token_id=model.config.eos_token_id,
        top_k=50,
        top_p=0.95,
    )
    gen_text.append(tokenizer.decode(output[0], skip_special_tokens=True))
    pass

with open('data/gnrt/fear3.csv', mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Text", "Emotion"])
    
    for text in gen_text:
        writer.writerow([text, "fear"])

print("finish.")