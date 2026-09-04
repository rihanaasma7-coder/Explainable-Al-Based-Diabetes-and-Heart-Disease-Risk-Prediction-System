import os
import pandas as pd
import joblib
from preprocessing import HEART_FEATURES

# Inspect dataset semantics
path = '/app/datasets/heart_disease.csv'
df = pd.read_csv(path)
print('dataset columns:', df.columns.tolist())
print('unique target values:', sorted(df['target'].unique().tolist()))
print('target counts:', df['target'].value_counts().to_dict())
for col in ['age', 'trestbps', 'chol', 'thalach', 'sex']:
    print(f'mean {col} by target:', df.groupby('target')[col].mean().to_dict())
print('\nmedian values by target:')
for col in ['age', 'trestbps', 'chol', 'thalach']:
    print(f'  {col}:', df.groupby('target')[col].median().to_dict())
print('\nvalue counts for target vs sex:')
print(df.groupby(['target', 'sex']).size())

print('\nTop high-risk candidate rows by age/chol/bp:')
print(df.sort_values(['age', 'chol', 'trestbps'], ascending=[False, False, False])[['age','sex','thalach','chol','trestbps','target']].head(20).to_string(index=False))
print('\nTop low-risk candidate rows by age/chol/bp:')
print(df.sort_values(['age', 'chol', 'trestbps'], ascending=[True, True, True])[['age','sex','thalach','chol','trestbps','target']].head(20).to_string(index=False))

# Load current model in container environment
bundle_path = '/app/models/heart_model.pkl'
print('\nmodel path:', bundle_path)
print('model exists:', os.path.exists(bundle_path))

if os.path.exists(bundle_path):
    bundle = joblib.load(bundle_path)
    model = bundle.pipeline.named_steps['model']
    print('bundle model name:', bundle.model_name)
    print('bundle model version:', bundle.model_version)
    print('classes_', model.classes_)
    print('type(model):', type(model))
    print('n_features_in_:', getattr(model, 'n_features_in_', None))
    
    healthy_resting = {'age':32,'gender':'Male','glucose':99,'bmi':24,'cholesterol':195,'bloodPressure':118,'heartRate':72}
    healthy_maxhr = {'age':32,'gender':'Male','glucose':99,'bmi':24,'cholesterol':195,'bloodPressure':118,'heartRate':170}
    high_risk = {'age':75,'gender':'Male','glucose':130,'bmi':38,'cholesterol':350,'bloodPressure':200,'heartRate':120}
    for label, case in [
        ('healthy_resting', healthy_resting),
        ('healthy_maxhr', healthy_maxhr),
        ('high_risk', high_risk),
    ]:
        df_case = pd.DataFrame([case])[HEART_FEATURES]
        probs = bundle.pipeline.predict_proba(df_case)[0].tolist()
        pred = bundle.pipeline.predict(df_case)[0]
        print(f'\n{label} case:')
        print('  input:', case)
        print('  predict_proba:', probs)
        print('  predict:', pred)
        print('  prob0 =', probs[0], 'prob1 =', probs[1])
else:
    print('Model file not found; cannot inspect classes.')
