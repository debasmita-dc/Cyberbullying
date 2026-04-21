import os
import pandas as pd
from sklearn.model_selection import train_test_split

# File paths
DATA_PATH = "data/train.csv"
TRAIN_OUT = "data/train_clean.csv"
VALID_OUT = "data/valid_clean.csv"

# Check file exists
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"❌ File not found: {DATA_PATH}")

# Load dataset
print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

print("Columns found:", df.columns.tolist())

# Combine toxic labels into single binary label
'''df["label"] = (
    (df["toxic"] == 1) |
    (df["severe_toxic"] == 1) |
    (df["obscene"] == 1) |
    (df["threat"] == 1) |
    (df["insult"] == 1) |
    (df["identity_hate"] == 1)
).astype(int)'''

labels = ["toxic","severe_toxic","obscene","threat","insult","identity_hate"]
df["labels"] = df[labels].values.tolist()
df["text"] = df["comment_text"].astype(str)
df = df[["text","labels"]]


# Text column
df["text"] = df["comment_text"].astype(str)

# Keep only needed columns
df = df[["text", "label"]]

# Remove empty rows
df = df.dropna()

print("\nTotal samples:", len(df))
print("Toxic samples:", df["label"].sum())
print("Non-toxic samples:", len(df) - df["label"].sum())

# Split dataset (IMPORTANT: stratify keeps balance)
train_df, valid_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df["label"]
)

# Save cleaned datasets
train_df.to_csv(TRAIN_OUT, index=False)
valid_df.to_csv(VALID_OUT, index=False)

print("\n✅ Dataset prepared successfully!")
print("Train samples:", len(train_df))
print("Validation samples:", len(valid_df))
print("\nFiles created:")
print(TRAIN_OUT)
print(VALID_OUT)
