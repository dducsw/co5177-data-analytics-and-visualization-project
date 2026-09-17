# Text & NLP: Best Practices & Reference Guide

## 1. Principles
- **Start with TF-IDF**: TF-IDF with LinearSVC or Logistic Regression takes seconds to train, runs on CPU, and sets an immediate high-water mark before trying Transformers.
- **Language-Aware Tokenization**: For non-segmented languages like Vietnamese, apply word segmentation (`pyvi` or `underthesea`) prior to $n$-gram extraction or classical models.
- **Transformers When Context Matters**: If subtle syntax, sentiment negation, or long-range semantics matter, fine-tune a pretrained encoder (`phobert-base`, `roberta-base`, `deberta-v3-small`).

## 2. Strong Classical Baseline (Fast & Effective)
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=25000, sublinear_tf=True)),
    ('clf', LogisticRegression(C=1.0, max_iter=1000, class_weight='balanced'))
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_val)
print(classification_report(y_val, y_pred))
```

## 3. Pretrained Transformer Fine-Tuning
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

model_name = "vinai/phobert-base-v2"  # or "roberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_classes)

training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    fp16=True  # Fast training on GPU
)
```

## 4. Error Analysis
- Print the Confusion Matrix normalized by true labels (`normalize='true'`).
- Inspect 5-10 specific misclassified texts to see whether errors stem from label noise, sarcasm, or missing vocabulary.
