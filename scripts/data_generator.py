import pandas as pd
import numpy as np
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.evaluation.single_table import evaluate_quality

def load_data(filepath):
    return pd.read_csv(filepath)

def detect_metadata(df):
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data=df)
    return metadata

def train_synthesizer(df, metadata):
    print("Training the synthesizer. This might take a moment.")
    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(df)
    print("Training complete!")
    return synthesizer

def generate_synthetic_data(synthesizer, num_rows=3000):
    print(f"Generating {num_rows} synthetic rows...")
    synthetic_data = synthesizer.sample(num_rows=num_rows)
    print("Generation Complete.")
    print(synthetic_data.head())
    return synthetic_data

def evaluate_data(real_data, synthetic_data, metadata):
    print("Evaluating statistical quality...")
    quality_report = evaluate_quality(
        real_data=real_data,
        synthetic_data=synthetic_data,
        metadata=metadata
    )
    print(quality_report)
    return quality_report

def inject_anomalies(df, pct=0.05):
    """
    Randomly selects a percentage of rows and injects statistically extreme 
    values into critical telemetry columns to simulate medical emergencies.
    Creates a ground-truth 'is_anomaly' label for downstream ML evaluation.
    """
    df['is_anomaly'] = False
    anomaly_indices = df.sample(frac=pct, random_state=42).index
    df.loc[anomaly_indices, 'is_anomaly'] = True
    
    midpoint = len(anomaly_indices) // 2
    
    high_anomalies = anomaly_indices[:midpoint]
    low_anomalies = anomaly_indices[midpoint:]
    
    df.loc[high_anomalies, 'Max Heart Rate'] = np.random.uniform(3.5, 5.0, len(high_anomalies))
    df.loc[high_anomalies, 'Resting Blood Pressure'] = np.random.uniform(3.5, 5.0, len(high_anomalies))
    
    df.loc[low_anomalies, 'Max Heart Rate'] = np.random.uniform(-5.0, -3.5, len(low_anomalies))
    df.loc[low_anomalies, 'Resting Blood Pressure'] = np.random.uniform(-5.0, -3.5, len(low_anomalies))
    
    return df

if __name__ == "__main__":
    print("1. Loading clean data...")
    df_input = load_data('./data/processed/cleaned_cleveland.csv')

    print("2. Detecting metadata...")
    metadata = detect_metadata(df_input)

    print("3. Training synthesizer (this takes a minute)...")
    synthesizer = train_synthesizer(df_input, metadata)

    print("4. Generating 3,000 synthetic rows...")
    synthetic_data = generate_synthetic_data(synthesizer, 3000)

    print("5. Evaluating quality...")
    evaluate_data(df_input, synthetic_data, metadata)

    print("6. Injecting anomalies...")
    synthetic_data = inject_anomalies(synthetic_data, pct=0.05)

    print("\n--- ANOMALY STATS ---")
    print(synthetic_data[synthetic_data['is_anomaly'] == True].describe())

    print("Converting the synthetic data into a csv file")
    synthetic_data.to_csv('./data/processed/synthetic_cleveland.csv', index=False)
    print("New synthetic data has been converted into a csv file")