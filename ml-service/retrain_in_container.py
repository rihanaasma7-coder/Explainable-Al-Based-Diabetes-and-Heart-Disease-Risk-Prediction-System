import os
from training import train_all_models

DATASET_DIR = os.getenv('DATASET_DIR', '/app/datasets')
MODEL_DIR = os.getenv('MODEL_DIR', '/app/models')

print('retraining with', DATASET_DIR, MODEL_DIR)
metrics = train_all_models(DATASET_DIR, MODEL_DIR)
print(metrics)
