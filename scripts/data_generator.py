import pandas as pd
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

if __name__ == "__main__":
    df_input = load_data('./data/processed/cleaned_cleveland.csv')
    metadata = detect_metadata(df_input)
    synthesizer = train_synthesizer(df_input, metadata)
    synthetic_data = generate_synthetic_data(synthesizer, 3000)
    evaluate_data(df_input, synthetic_data, metadata)
    synthetic_data.to_csv('./data/processed/synthetic_cleveland.csv', index=False)