import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from xgboost import XGBClassifier

path = os.path.join('..','datasets','heart_disease.csv')
df = pd.read_csv(path)
df = df.rename(columns={'sex':'gender','trestbps':'bloodPressure','chol':'cholesterol','thalach':'heartRate','fbs':'fbs'})

df['gender'] = df['gender'].map({1:'Male',0:'Female'})
df['glucose'] = df['fbs']*45 + 95
df['bmi'] = 27
features = ['age','gender','cholesterol','bloodPressure','heartRate']
X = df[features]
y = df['target']

preprocessor = ColumnTransformer([('num', Pipeline([('scaler', StandardScaler())]), ['age','cholesterol','bloodPressure','heartRate']), ('cat', OneHotEncoder(handle_unknown='ignore'),['gender'])])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model = XGBClassifier(n_estimators=180,max_depth=4,learning_rate=0.05,subsample=0.9,colsample_bytree=0.9,eval_metric='logloss',random_state=42)
pipe = Pipeline([('pre', preprocessor), ('model', model)])
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
print('acc', accuracy_score(y_test, y_pred), 'f1', f1_score(y_test,y_pred), 'recall', recall_score(y_test,y_pred))
case = {'age':65,'gender':'Male','cholesterol':290,'bloodPressure':170,'heartRate':105}
print('case prob', pipe.predict_proba(pd.DataFrame([case]))[0][1])
for v in [110,200]:
    c = case.copy(); c['bloodPressure']=v
    print('bp', v, pipe.predict_proba(pd.DataFrame([c]))[0][1])
for v in [150,350]:
    c = case.copy(); c['cholesterol']=v
    print('chol', v, pipe.predict_proba(pd.DataFrame([c]))[0][1])
for v in [60,130]:
    c = case.copy(); c['heartRate']=v
    print('hr', v, pipe.predict_proba(pd.DataFrame([c]))[0][1])
