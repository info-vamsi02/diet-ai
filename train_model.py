import os
import pandas as pd
import torch
import pickle

from sklearn.preprocessing import LabelEncoder
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments

# create folder
os.makedirs("saved_model", exist_ok=True)

# load dataset
data = pd.read_csv("diet_recommendations_dataset.csv")

# ---------------- FIX INPUT TEXT ----------------
# REMOVE glucose and ADD gender

data["text"] = data.apply(
    lambda x: f"Age {x.Age}, Gender {x.Gender}, BMI {x.BMI}, Disease {x.Disease_Type}, Activity {x.Physical_Activity_Level}",
    axis=1
)

# labels
labels = data["Diet_Recommendation"]

# encode labels
le = LabelEncoder()
labels = le.fit_transform(labels)

# save encoder
pickle.dump(le, open("saved_model/label_encoder.pkl", "wb"))

# tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

encodings = tokenizer(
    list(data["text"]),
    truncation=True,
    padding=True,
    max_length=64
)

# dataset class
class DietDataset(torch.utils.data.Dataset):

    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

dataset = DietDataset(encodings, labels)

# model
model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=len(set(labels))
)

# training args
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=8
)

# trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset
)

# train
trainer.train()

# save model
model.save_pretrained("saved_model")
tokenizer.save_pretrained("saved_model")