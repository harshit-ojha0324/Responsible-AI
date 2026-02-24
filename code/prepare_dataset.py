import os
import pandas as pd
from datasets import load_dataset
import numpy as np

def create_directories():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dirs = [
        os.path.join(base_dir, "data", "raw"),
        os.path.join(base_dir, "data", "processed"),
        os.path.join(base_dir, "data", "annotations"),
        os.path.join(base_dir, "outputs"),
        os.path.join(base_dir, "results"),
        os.path.join(base_dir, "notebooks"),
        os.path.join(base_dir, "scripts")
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Ensured directory exists: {d}")

def prepare_dataset(sample_size=200, seed=42):
    print("Loading GSM8K dataset...")
    # Load GSM8K 'main' config
    ds = load_dataset("openai/gsm8k", "main")
    
    # Use test set for evaluation as per plan (usually we evaluate on test, but plan says "Sample 150-200 problems from test set")
    test_ds = ds['test']
    
    print(f"Total test examples: {len(test_ds)}")
    
    # Convert to pandas for easier sampling
    df = pd.DataFrame(test_ds)
    
    # Stratified sampling if possible (by difficulty/length). 
    # GSM8K doesn't have explicit difficulty, so we can use answer length or question length as proxy.
    # For now, simple random sampling with seed is fine as a start, or we can bin by length.
    
    # Calculate length of solution
    df['solution_length'] = df['answer'].apply(len)
    
    # Sample
    print(f"Sampling {sample_size} examples...")
    sampled_df = df.sample(n=sample_size, random_state=seed)
    
    # Add an ID
    sampled_df['problem_id'] = [f"gsm8k_{i:03d}" for i in range(len(sampled_df))]
    
    # Select columns
    final_df = sampled_df[['problem_id', 'question', 'answer']]
    
    # Save to CSV
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, "data", "dataset_manifest.csv")
    final_df.to_csv(output_path, index=False)
    
    print(f"Saved dataset manifest to {output_path}")
    print(final_df.head())

if __name__ == "__main__":
    create_directories()
    prepare_dataset()
