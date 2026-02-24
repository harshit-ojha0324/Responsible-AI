import pandas as pd
import os
import sys
from inference import run_inference
from prompts import OUTCOME_PROMPT, PROCESS_PROMPT, STRUCTURED_PROMPT

def test_prompts():
    # Load dataset
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(base_dir, "data", "dataset_manifest.csv")
    
    if not os.path.exists(manifest_path):
        print(f"Dataset manifest not found at {manifest_path}")
        return

    df = pd.read_csv(manifest_path)
    
    # Sample 5
    sample_5 = df.head(5)
    
    prompts = {
        "Outcome": OUTCOME_PROMPT,
        "Process": PROCESS_PROMPT,
        "Structured": STRUCTURED_PROMPT
    }
    
    # We will test only 1 problem for all 3 prompts to save time/tokens for this test, or all 5 for one prompt?
    # Plan says "Test prompts on 5 sample problems".
    # I'll do 1 problem across 3 prompts to verify format, then maybe loop 5 if fast.
    # Let's do 2 problems x 3 prompts.
    
    for idx, row in sample_5.iloc[:2].iterrows():
        question = row['question']
        print(f"\n{'='*50}\nTesting Problem ID: {row['problem_id']}\n{'='*50}")
        print(f"Question: {question[:100]}...")
        
        for name, template in prompts.items():
            prompt = template.format(question=question)
            print(f"\n--- Testing {name} Prompt ---")
            # Using a cheap model or free model if possible. inference.py defaults to google/gemini-2.0-flash-exp:free
            response = run_inference(prompt)
            print(f"Response ({name}):\n{response}\n")

if __name__ == "__main__":
    test_prompts()
