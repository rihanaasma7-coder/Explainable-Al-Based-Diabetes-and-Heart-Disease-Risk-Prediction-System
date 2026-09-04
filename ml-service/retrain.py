import os
from training import train_all_models
MODEL_DIR = os.path.join('..', 'models')
DATASET_DIR = os.path.join('..', 'datasets')
metrics = train_all_models(DATASET_DIR, MODEL_DIR)
print(metrics)
