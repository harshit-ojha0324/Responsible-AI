import os
import json
import pandas as pd
import time
from tqdm import tqdm
from inference import run_inference
from prompts import OUTCOME_PROMPT, PROCESS_PROMPT, STRUCTURED_PROMPT

# Configuration
INPUT_MANIFEST = "../data/dataset_manifest.csv"
OUTPUT_FILE = "../data/raw/responses.jsonl"
SAVE_INTERVAL = 5  # Save every 5 problems
MODEL_NAME = "x-ai/grok-4.1-fast"

def load_manifest():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(base_dir, INPUT_MANIFEST)
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest not found at {manifest_path}")
    return pd.read_csv(manifest_path)

def load_existing_progress():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)
    if not os.path.exists(output_path):
        return set()
    
    existing_ids = set()
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                existing_ids.add(data["problem_id"])
            except json.JSONDecodeError:
                continue
    return existing_ids

def generate_responses():
    df = load_manifest()
    existing_ids = load_existing_progress()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)
    
    print(f"Loaded {len(df)} problems.")
    print(f"Found {len(existing_ids)} already processed.")
    
    problems_to_process = df[~df["problem_id"].isin(existing_ids)]
    print(f"Remaining to process: {len(problems_to_process)}")
    
    if len(problems_to_process) == 0:
        print("All problems processed.")
        return

    for idx, row in tqdm(problems_to_process.iterrows(), total=len(problems_to_process)):
        problem_id = row["problem_id"]
        question = row["question"]
        ground_truth = row["answer"]
        
        result = {
            "problem_id": problem_id,
            "question": question,
            "ground_truth": ground_truth,
            "model": MODEL_NAME,
            "responses": {}
        }
        
        try:
            # 1. Outcome Condition
            outcome_prompt = OUTCOME_PROMPT.format(question=question)
            outcome_res = run_inference(outcome_prompt, model=MODEL_NAME)
            result["responses"]["outcome"] = outcome_res
            time.sleep(1) # Rate limit politeness

            # 2. Process Condition
            process_prompt = PROCESS_PROMPT.format(question=question)
            process_res = run_inference(process_prompt, model=MODEL_NAME)
            result["responses"]["process"] = process_res
            time.sleep(1)

            # 3. Structured Condition
            structured_prompt = STRUCTURED_PROMPT.format(question=question)
            structured_res = run_inference(structured_prompt, model=MODEL_NAME)
            result["responses"]["structured"] = structured_res
            time.sleep(1)
            
            # Save line
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(result) + "\n")
                
        except Exception as e:
            print(f"Error processing {problem_id}: {e}")
            continue

if __name__ == "__main__":
    generate_responses()
