import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import json

df = pd.read_csv('./data/raw/heart+disease/processed.cleveland.data', header=None, encoding='unicode_escape')
df.columns = ['Age', 'Sex', 'Chest-Pain Type', 'Resting Blood Pressure', 'Serum Cholestrol in md/dl',
          'Fasting Blood Sugar > 120mg/dl', 'Resting electrocardiographic results', 'Max Heart Rate', 'Exercise Induced Angina',
          'ST Depression Induced', 'Slope of the peak exercise ST Segment', 'Number of Major Vessels', 'Thal',
          'Diagnosis of Heart Disease']
df = df.replace('?', np.nan)
df['Number of Major Vessels'] = pd.to_numeric(df['Number of Major Vessels'], errors='coerce')
df['Thal'] = pd.to_numeric(df['Thal'], errors='coerce')
df['Number of Major Vessels'] = df['Number of Major Vessels'].fillna(df['Number of Major Vessels'].median())
df['Thal'] = df['Thal'].fillna(df['Thal'].median())
df['Serum Cholestrol in md/dl'] = np.log1p(df['Serum Cholestrol in md/dl'])
df['Resting Blood Pressure'] = np.log1p(df['Resting Blood Pressure'])

scaler = StandardScaler()
continuous_columns = ['Age', 'Resting Blood Pressure', 'Serum Cholestrol in md/dl',
                      'Max Heart Rate', 'ST Depression Induced', 'Number of Major Vessels']
scaler.fit(df[continuous_columns])

params = {
    'means': dict(zip(continuous_columns, scaler.mean_.tolist())),
    'stds': dict(zip(continuous_columns, scaler.scale_.tolist()))
}
print(json.dumps(params, indent=2))