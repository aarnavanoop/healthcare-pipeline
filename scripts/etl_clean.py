import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


def load_data(filepath):
    '''Loads the CSV, assigns column names, replaces ? with NaN, and returns the dataframe. '''
    df = pd.read_csv(filepath, header=None,encoding='unicode_escape')
    df.columns = ['Age', 'Sex', 'Chest-Pain Type', 'Resting Blood Pressure', 'Serum Cholestrol in md/dl',
              'Fasting Blood Sugar > 120mg/dl', 'Resting electrocardiographic results', 'Max Heart Rate', 'Exercise Induced Angina',
              'ST Depression Induced', 'Slope of the peak exercise ST Segment', 'Number of Major Vessels', 'Thal',
              'Diagnosis of Heart Disease']
    df = df.replace('?', np.nan)
    return df


def fix_object_columns(df):
    '''Replace Null values and convert the columns of type object into type float'''
    df['Number of Major Vessels'] = pd.to_numeric(df['Number of Major Vessels'], errors = 'coerce')
    df['Thal'] = pd.to_numeric(df['Thal'], errors = 'coerce')
    df['Number of Major Vessels'] = df['Number of Major Vessels'].fillna(df['Number of Major Vessels'].median())
    df['Thal'] = df['Thal'].fillna(df['Thal'].median())
    return df


def fix_target_column(df):
    '''Fix Target Columns, mapping the spread of values that ranged from 0 - 4 to binary values'''
    replacement_mapping = {0: 0,
                       1: 1,
                       2: 1,
                       3: 1,
                       4: 1}
    df['Diagnosis of Heart Disease'] = df['Diagnosis of Heart Disease'].replace(replacement_mapping)
    return df

def encode_categorical_columns(df):
    '''Applies get_dummies to categorical columns and returns the updated df'''
    columns_to_encode = ['Chest-Pain Type', 'Resting electrocardiographic results', 'Thal', 'Slope of the peak exercise ST Segment' ]
    df = pd.get_dummies(df, columns = columns_to_encode, drop_first = True, dtype = int)
    return df

def handle_outliers(df):
    '''Remove outliers in the continuous columns using np.log1p'''
    df['Serum Cholestrol in md/dl'] = np.log1p(df['Serum Cholestrol in md/dl'])
    df['Resting Blood Pressure'] = np.log1p(df['Resting Blood Pressure'])
    return df

def normalise_continuous_columns(df):
    '''Normalise columns that have numerical data'''
    scaler = StandardScaler()
    continuous_columns = ['Age', 'Resting Blood Pressure', 'Serum Cholestrol in md/dl', 'Max Heart Rate',
                        'ST Depression Induced', 'Number of Major Vessels',]
    df[continuous_columns] = scaler.fit_transform(df[continuous_columns])
    print(df[continuous_columns].head())
    return df

def verify_clean_data(df):
    """Prints isnull sum, info, describe, value counts on target, and row count as a sanity check."""
    print("--- Null Values ---")
    print(df.isnull().sum())
    print("\n--- Data Info ---")
    df.info()
    print("\n--- Target Column Distribution ---")
    print(df['Diagnosis of Heart Disease'].value_counts())
    print("\n--- Statistics ---")
    print(df.describe())
    print(f"\nRow count: {len(df)}")

if __name__ == "__main__":
    df = load_data('./heart+disease/processed.cleveland.data')
    df = fix_object_columns(df)
    df = fix_target_column(df)
    df = encode_categorical_columns(df)
    df = handle_outliers(df)
    df = normalise_continuous_columns(df)
    verify_clean_data(df)
    df.to_csv('cleaned_cleveland.csv', index=False)
    print("ETL complete. Cleaned data saved.")

