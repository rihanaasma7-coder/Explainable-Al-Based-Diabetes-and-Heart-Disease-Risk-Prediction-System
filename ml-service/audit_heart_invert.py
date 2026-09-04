import os
import pandas as pd
from preprocessing import preprocess_heart, HEART_FEATURES
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, recall_score
from xgboost import XGBClassifier

dataset_dir = os.path.join('..','datasets')
processed_dir = os.path.join('..','processed')
X, y, pipe = preprocess_heart(dataset_dir, processed_dir)
print('y value counts', y.value_counts().to_dict())
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
for desc, ytr in [('original', y_train), ('flipped', 1 - y_train)]:
    model = XGBClassifier(n_estimators=180, max_depth=4, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, eval_metric='logloss', random_state=42, scale_pos_weight=1.0)
    pipe_i = Pipeline([('features', pipe), ('model', model)])
    pipe_i.fit(X_train, ytr)
    if desc == 'original':
        y_pred = pipe_i.predict(X_test)
        print('orig metrics', accuracy_score(y_test, y_pred), f1_score(y_test, y_pred), recall_score(y_test, y_pred))
        case = {'age':65,'gender':'Male','glucose':110,'bmi':29,'cholesterol':290,'bloodPressure':170,'heartRate':105}
        prob = pipe_i.predict_proba(pd.DataFrame([case])[HEART_FEATURES])[0][1]
        print('orig case prob', prob)
    else:
        y_pred = pipe_i.predict(X_test)
        print('flipped metrics', accuracy_score(1-y_test, y_pred), f1_score(1-y_test, y_pred), recall_score(1-y_test, y_pred))
        case = {'age':65,'gender':'Male','glucose':110,'bmi':29,'cholesterol':290,'bloodPressure':170,'heartRate':105}
        prob = pipe_i.predict_proba(pd.DataFrame([case])[HEART_FEATURES])[0][1]
        print('flipped case prob', prob)
