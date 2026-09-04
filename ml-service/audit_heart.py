import os
import numpy as np
import pandas as pd
from preprocessing import preprocess_heart, HEART_FEATURES
from training import candidate_models
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, recall_score
from xgboost import XGBClassifier
import shap

print('cwd', os.getcwd())
dataset_dir = os.path.join('..','datasets')
processed_dir = os.path.join('..','processed')
X, y, pipe = preprocess_heart(dataset_dir, processed_dir)
print('features', X.columns.tolist())
print('X shape', X.shape)
print('y distribution', y.value_counts().to_dict())
print('Bmi unique', X['bmi'].unique()[:10], 'nunique', X['bmi'].nunique())
print('chol range', X['cholesterol'].min(), X['cholesterol'].max())
print('bp range', X['bloodPressure'].min(), X['bloodPressure'].max())
print('hr range', X['heartRate'].min(), X['heartRate'].max())
print('Value counts gender', X['gender'].value_counts().to_dict())
print('\ncorrelations with target:')
X_corr = pd.get_dummies(X, columns=['gender'], drop_first=True)
print(X_corr.assign(target=y).corr()['target'].drop('target'))
print('\nmean values by target:')
print(X_corr.assign(target=y).groupby('target').mean().T)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
for name, model in candidate_models(1.0).items():
    pipe_i = Pipeline([('features', pipe), ('model', model)])
    pipe_i.fit(X_train, y_train)
    y_pred = pipe_i.predict(X_test)
    print(f'\n{name} metrics: acc {accuracy_score(y_test, y_pred):.4f} f1 {f1_score(y_test, y_pred):.4f} recall {recall_score(y_test, y_pred):.4f}')
    if hasattr(model, 'coef_'):
        print(' coef', model.coef_)
    if hasattr(model, 'feature_importances_'):
        print(' feature_importances', model.feature_importances_)

xgb = XGBClassifier(n_estimators=180, max_depth=4, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, eval_metric='logloss', random_state=42, scale_pos_weight=1.0)
pipe_xgb = Pipeline([('features', pipe), ('model', xgb)])
pipe_xgb.fit(X_train, y_train)

transformed_names = pipe_xgb.named_steps['features'].get_feature_names_out()
print('\ntransformed feature names:', transformed_names)
print('feature importances:', xgb.feature_importances_)
print('bp features', [(n, v) for n, v in zip(transformed_names, xgb.feature_importances_) if 'bloodPressure' in n])
print('chol features', [(n, v) for n, v in zip(transformed_names, xgb.feature_importances_) if 'cholesterol' in n])
print('heartRate features', [(n, v) for n, v in zip(transformed_names, xgb.feature_importances_) if 'heartRate' in n])
print('age features', [(n, v) for n, v in zip(transformed_names, xgb.feature_importances_) if 'age' in n])
print('glucose features', [(n, v) for n, v in zip(transformed_names, xgb.feature_importances_) if 'glucose' in n])
print('bmi features', [(n, v) for n, v in zip(transformed_names, xgb.feature_importances_) if 'bmi' in n])
print('gender features', [(n, v) for n, v in zip(transformed_names, xgb.feature_importances_) if 'gender' in n])

case = {'age':65,'gender':'Male','glucose':110,'bmi':29,'cholesterol':290,'bloodPressure':170,'heartRate':105}
frame = pd.DataFrame([case])[HEART_FEATURES]
prob = pipe_xgb.predict_proba(frame)[0][1]
print('\ncase prob', prob)
for v in [110, 200]:
    c = case.copy(); c['bloodPressure']=v
    print('bp', v, pipe_xgb.predict_proba(pd.DataFrame([c])[HEART_FEATURES])[0][1])
for v in [150, 350]:
    c = case.copy(); c['cholesterol']=v
    print('chol', v, pipe_xgb.predict_proba(pd.DataFrame([c])[HEART_FEATURES])[0][1])
for v in [60, 130]:
    c = case.copy(); c['heartRate']=v
    print('hr', v, pipe_xgb.predict_proba(pd.DataFrame([c])[HEART_FEATURES])[0][1])

# SHAP on transformed features
transformed_frame = pipe_xgb.named_steps['features'].transform(frame)
explainer = shap.TreeExplainer(pipe_xgb.named_steps['model'])
shap_values = explainer(transformed_frame)
print('\nSHAP values shape', shap_values.values.shape)
print('SHAP values', shap_values.values)
print('SHAP base values', shap_values.base_values)
print('expected value', shap_values.expected_value)
print('sum shap + base equals logit??', shap_values.values.sum() + shap_values.base_values)
