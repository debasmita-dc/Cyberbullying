import os
import numpy as np
import pandas as pd

from datasets import Dataset
from sklearn.model_selection import train_test_split

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

import evaluate

# -------------------------
# SETTINGS
# -------------------------
MODEL_NAME = "distilbert-base-uncased"  # faster than bert-base
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 2
LR = 2e-5

DATA_PATH = os.path.join("data", "train.csv")  # Jigsaw train.csv
SAVE_DIR = os.path.abspath(os.path.join("..", "models", "toxicity-bert"))


# -------------------------
# METRICS
# -------------------------
acc = evaluate.load("accuracy")
f1 = evaluate.load("f1")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": acc.compute(predictions=preds, references=labels)["accuracy"],
        "f1": f1.compute(predictions=preds, references=labels, average="binary")["f1"],
    }


# -------------------------
# MAIN
# -------------------------
def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Not found: {DATA_PATH}. Make sure ml/data/train.csv exists.")

    print("✅ Loading:", DATA_PATH)
    df = pd.read_csv(DATA_PATH)

    # --- Jigsaw columns ---
    # comment_text + toxic/severe_toxic/obscene/threat/insult/identity_hate
    required = ["comment_text", "toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"❌ Your train.csv doesn't look like Jigsaw train.csv.\nMissing columns: {missing}\n"
            f"Found columns: {df.columns.tolist()}"
        )

    # Build a single binary label: 1 if any toxic category is 1, else 0
    df["label"] = (
        (df["toxic"] == 1) |
        (df["severe_toxic"] == 1) |
        (df["obscene"] == 1) |
        (df["threat"] == 1) |
        (df["insult"] == 1) |
        (df["identity_hate"] == 1)
    ).astype(int)

    df["text"] = df["comment_text"].astype(str)
    df = df[["text", "label"]].dropna()

    # Optional: reduce size for faster training (comment out if you want full dataset)
    df = df.sample(n=20000, random_state=42)

    train_df, valid_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["label"])

    train_ds = Dataset.from_pandas(train_df.reset_index(drop=True))
    valid_ds = Dataset.from_pandas(valid_df.reset_index(drop=True))

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=MAX_LEN
        )

    train_ds = train_ds.map(tokenize, batched=True)
    valid_ds = valid_ds.map(tokenize, batched=True)

    train_ds = train_ds.rename_column("label", "labels")
    valid_ds = valid_ds.rename_column("label", "labels")

    cols = ["input_ids", "attention_mask", "labels"]
    train_ds = train_ds.select_columns(cols)
    valid_ds = valid_ds.select_columns(cols)

    model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=6,
    problem_type="multi_label_classification"
)

#model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    args = TrainingArguments(
        output_dir="runs/toxicity",
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=50,
        learning_rate=LR,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=EPOCHS,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        compute_metrics=compute_metrics
    )

    print("🚀 Training started...")
    trainer.train()

    # Save final model
    os.makedirs(SAVE_DIR, exist_ok=True)
    trainer.save_model(SAVE_DIR)
    tokenizer.save_pretrained(SAVE_DIR)

    print("\n✅ Training complete!")
    print("✅ Model saved to:", SAVE_DIR)
    print("Now your Flask backend should load from this folder.")


if __name__ == "__main__":
    main()
