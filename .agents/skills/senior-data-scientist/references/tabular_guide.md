# Tabular Data: Best Practices & Reference Guide

## 1. Principles
- **Simplicity First**: A well-tuned GBDT (`LightGBM` or `CatBoost`) beats complex neural nets on 90%+ of tabular datasets with 10x less compute and tuning time.
- **Leak-Free Pipeline**: Always compute statistics (mean, median, encodings, scales) strictly on the training folds. Never fit on the full dataset before splitting.
- **Handling Imbalance**:
  - Do not use accuracy. Use PR-AUC (Average Precision) and F1-score.
  - Set class weights (`scale_pos_weight` in LightGBM/XGBoost, `auto_class_weights='Balanced'` in CatBoost).
  - Tune classification thresholds instead of blindly defaulting to 0.5.

## 2. Standard GBDT Baseline with Stratified K-Fold
```python
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, average_precision_score
import lightgbm as lgb

def train_lgb_cv(X, y, num_cols, cat_cols, n_splits=5):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    oof_preds = np.zeros(len(X))
    
    # Cast categorical columns
    for c in cat_cols:
        X[c] = X[c].astype('category')
        
    scale_pos = (len(y) - sum(y)) / sum(y)
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_va, y_va = X.iloc[val_idx], y.iloc[val_idx]
        
        model = lgb.LGBMClassifier(
            n_estimators=1000,
            learning_rate=0.03,
            scale_pos_weight=scale_pos,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(
            X_tr, y_tr,
            eval_set=[(X_va, y_va)],
            callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)]
        )
        oof_preds[val_idx] = model.predict_proba(X_va)[:, 1]
        
    print(f"OOF ROC-AUC: {roc_auc_score(y, oof_preds):.4f}")
    print(f"OOF PR-AUC:  {average_precision_score(y, oof_preds):.4f}")
    return oof_preds
```

## 3. Explainability
- Use SHAP TreeExplainer for feature importance and interaction insights:
```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_val)
shap.summary_plot(shap_values, X_val)
```
