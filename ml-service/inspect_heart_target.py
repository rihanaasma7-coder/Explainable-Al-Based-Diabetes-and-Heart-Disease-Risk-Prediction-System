import os
import pandas as pd
from preprocessing import preprocess_heart, HEART_FEATURES

DATASET_DIR = '/app/datasets'
PROCESSED_DIR = '/app/processed'

# Inspect raw dataset
raw = pd.read_csv(os.path.join(DATASET_DIR, 'heart_disease.csv'))
print('raw columns:', raw.columns.tolist())
print('raw target unique:', sorted(raw['target'].unique().tolist()))
print('raw target counts:', raw['target'].value_counts().to_dict())
print('raw target means by heartRate:', raw.groupby('target')['thalach'].mean().to_dict())
print('raw target means by age:', raw.groupby('target')['age'].mean().to_dict())
print('raw target means by chol:', raw.groupby('target')['chol'].mean().to_dict())
print('raw target means by trestbps:', raw.groupby('target')['trestbps'].mean().to_dict())

X, y, pipeline = preprocess_heart(DATASET_DIR, PROCESSED_DIR)
print('\nprocessed X shape:', X.shape)
print('processed y unique:', sorted(y.unique().tolist()))
print('processed y counts:', y.value_counts().to_dict())
print('processed y mean by age:', X.assign(target=y).groupby('target')['age'].mean().to_dict())
print('processed y mean by chol:', X.assign(target=y).groupby('target')['cholesterol'].mean().to_dict())
print('processed y mean by trestbps:', X.assign(target=y).groupby('target')['bloodPressure'].mean().to_dict())
print('processed y mean by heartRate:', X.assign(target=y).groupby('target')['heartRate'].mean().to_dict())
print('\nfirst 5 processed rows:')
print(X.assign(target=y).head().to_string(index=False))
