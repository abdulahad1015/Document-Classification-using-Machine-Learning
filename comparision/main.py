#!/usr/bin/env python3
# CNIC vs Not-CNIC Classification Pipeline
# Includes BERT fine-tuning + Gemini LLM evaluation

import pandas as pd
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from sklearn.metrics import classification_report
import google.generativeai as genai

# ============================================================
# 1. Load Dataset
# ============================================================
# Your CSV must contain: text,label
# Example:
# "Government of Pakistan CNIC #...",cnic
# "Invoice #223...",not_cnic

print("Loading dataset...")
dataset = load_dataset('csv', data_files='cnic_data.csv')['train']
dataset = dataset.train_test_split(test_size=0.2)
train_ds, test_ds = dataset['train'], dataset['test']

print(f"Training samples: {len(train_ds)}")
print(f"Testing samples: {len(test_ds)}")

# ============================================================
# 2. BERT Fine-Tuning (DistilBERT)
# ============================================================

print("\nPreparing BERT tokenizer...")
model_name = 'distilbert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize(batch):
    return tokenizer(batch['text'], truncation=True, padding=True)

train_tok = train_ds.map(tokenize, batched=True)
test_tok = test_ds.map(tokenize, batched=True)

print("Loading DistilBERT model...")
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2
)

args = TrainingArguments(
    output_dir='bert_cnic',
    num_train_epochs=10,              # higher due to small dataset
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    warmup_steps=10,
    learning_rate=3e-5,
    evaluation_strategy='epoch',
    logging_strategy="epoch",
    save_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_tok,
    eval_dataset=test_tok
)

print("\nTraining BERT...")
trainer.train()

print("\nEvaluating BERT...")
bert_metrics = trainer.evaluate()
print("\n====== BERT Evaluation Metrics ======")
print(bert_metrics)

# ============================================================
# 3. Gemini LLM Classification
# ============================================================

print("\nConfiguring Gemini...")

# Insert your Gemini API key here
genai.configure(api_key="YOUR_GEMINI_API_KEY")

model_g = genai.GenerativeModel("gemini-1.5-flash")

def classify_gemini(text):
    prompt = f"""
You are a strict binary classifier.
Classify the following OCR text as either 'cnic' or 'not_cnic'.
Return ONLY one word: cnic or not_cnic.

Text:
{text}
"""
    try:
        out = model_g.generate_content(prompt)
        return out.text.strip().lower()
    except Exception as e:
        print("Gemini error:", e)
        return "not_cnic"


y_true = []
y_pred = []

print("\nRunning Gemini classification on test dataset...")
for row in test_ds:
    true_label = row['label'].lower()
    pred_label = classify_gemini(row['text'])

    y_true.append(true_label)
    y_pred.append(pred_label)

print("\n====== Gemini LLM Classification Report ======")
print(classification_report(y_true, y_pred))

print("\nDONE.")
