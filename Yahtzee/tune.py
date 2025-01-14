from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
import json
import torch
from torch.utils.data import Dataset

model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_name, device_map="cpu")

class ConversationDataset(Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        item['labels'] = item['input_ids'].clone()
        return item

    def __len__(self):
        return len(self.encodings.input_ids)

def load_dataset(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['conversations']

def preprocess_conversations(conversations):
    dataset = []
    for convo in conversations:
        question = convo['question']
        answer = convo['answer']
        dataset.append(f"User: {question}\nBot: {answer}")
    return tokenizer(dataset, truncation=True, padding=True, max_length=512, return_tensors="pt")

conversations = load_dataset('db.json')
train_encodings = preprocess_conversations(conversations)
train_dataset = ConversationDataset(train_encodings)

training_args = TrainingArguments(
    output_dir="./fine_tuned_model",
    num_train_epochs=100,
    per_device_train_batch_size=1,
    save_steps=500,
    save_total_limit=2,
    logging_dir='./logs',
    logging_steps=100,
    no_cuda=True,
    learning_rate=1e-4,
    gradient_accumulation_steps=4,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()

model.save_pretrained("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")