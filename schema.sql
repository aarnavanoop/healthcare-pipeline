CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS healthcare_data;

CREATE TABLE healthcare_data.patients (
   patient_id UUID PRIMARY KEY,
   age FLOAT NOT NULL,
   sex INT NOT NULL,
   resting_blood_pressure FLOAT NOT NULL,
   serum_cholestrol FLOAT NOT NULL,
   fasting_blood_sugar INT NOT NULL,
   max_heart_rate FLOAT NOT NULL,
   exercise_induced_angina INT NOT NULL,
   st_depression_induced FLOAT NOT NULL,
   number_of_vessels FLOAT NOT NULL,
   diagnosis_of_disease INT NOT NULL,
   "chest_pain_2.0" INT NOT NULL,
   "chest_pain_3.0" INT NOT NULL,
   "chest_pain_4.0" INT NOT NULL,
   "resting_ecg_1.0" INT NOT NULL,
   "resting_ecg_2.0" INT NOT NULL,
   "thal_6.0" INT NOT NULL,
   "thal_7.0" INT NOT NULL,
   "slope_peak_2.0" INT NOT NULL,
   "slope_peak_3.0" INT NOT NULL,
   is_anomaly BOOLEAN NOT NULL
);

CREATE TABLE healthcare_data.patient_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES healthcare_data.patients(patient_id),
    note_text TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE healthcare_data.rag_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    context_notes TEXT NOT NULL,
    response_text TEXT NOT NULL,
    latency_ms FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);