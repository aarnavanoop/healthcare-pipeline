import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()


DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = "db"  
DB_PORT = "5432"
DB_NAME = os.getenv("POSTGRES_DB", "postgres")

def load_data():
    print("1. Loading synthetic data from CSV...")
    df = pd.read_csv('./data/processed/synthetic_cleveland.csv')

    print("1.5 Renaming columns to match database schema...")
    df = df.rename(columns={
        'Age': 'age',
        'Sex': 'sex',
        'Resting Blood Pressure': 'resting_blood_pressure',
        'Serum Cholestrol in md/dl': 'serum_cholestrol',
        'Fasting Blood Sugar > 120mg/dl': 'fasting_blood_sugar',
        'Max Heart Rate': 'max_heart_rate',
        'Exercise Induced Angina': 'exercise_induced_angina',
        'ST Depression Induced': 'st_depression_induced',
        'Number of Major Vessels': 'number_of_vessels',
        'Diagnosis of Heart Disease': 'diagnosis_of_disease',
        'Chest-Pain Type_2.0': 'chest_pain_2.0',
        'Chest-Pain Type_3.0': 'chest_pain_3.0',
        'Chest-Pain Type_4.0': 'chest_pain_4.0',
        'Resting electrocardiographic results_1.0': 'resting_ecg_1.0',
        'Resting electrocardiographic results_2.0': 'resting_ecg_2.0',
        'Thal_6.0': 'thal_6.0',
        'Thal_7.0': 'thal_7.0',
        'Slope of the peak exercise ST Segment_2.0': 'slope_peak_2.0',
        'Slope of the peak exercise ST Segment_3.0': 'slope_peak_3.0'
    })

    engine_url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(engine_url)

    try:
        print("2. Attempting to connect and insert data into PostgreSQL...")
        df.to_sql('patients', engine, schema='healthcare_data', if_exists='append', index=False)
        print("3. Success! 3000 rows loaded into the database.")
        
    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
if __name__ == "__main__":
    load_data()